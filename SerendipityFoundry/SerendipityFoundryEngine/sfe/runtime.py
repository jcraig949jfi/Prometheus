"""The Gen-2 Foundry runtime: the authoritative facade over the SQLite store.

Every mutating operation runs in one write transaction that changes state AND
appends the corresponding event atomically (invariants I4/I9: evidence is
immutable and the Foundry -- not an agent -- records what happened). Ownership
is checked on every world-scoped operation (I5: isolation by default; knowing an
id does not grant access). Open one Foundry per thread/worker.
"""

from __future__ import annotations

import hashlib
import json
import secrets
import random
from typing import Any, Optional

from sfe import events
from sfe import release
from sfe.errors import (AccessDenied, BudgetExhausted, ConflictError,
                         InvalidTransition, IsolationViolation, NotFound,
                         PredictionOrderingError, ValidationError)
from sfe.ids import (content_hash, engine_id_from_key, key_fingerprint,
                     new_id, session_key_for, sha256_hex)
from sfe.store import SCHEMA_VERSION, Store, now


def _sha(x: str) -> str:
    """SHA-256 of a bearer-like secret. Mirrors _token_hash in api.py:
    the plaintext is never stored."""
    return sha256_hex(x.encode())

# The closed info_kind ontology the sharing machinery understands. An artifact's
# meta may carry arbitrary freeform user metadata, but info_kind is CONTROL
# configuration and must come from this vocabulary (DFX-4 discipline).
#
# F2 (GEN-2.1): "success" is a FIRST-CLASS kind, not a synonym for "artifact".
# Before GEN-2.1 the SUCCESSES_ONLY policy pointed at "artifact", so a policy
# named for successes actually shared every artifact (incoherent -- an artifact
# can be produced for a failed line too). Now a producer that wants to share a
# validated result tags it info_kind="success" explicitly; SUCCESSES_ONLY shares
# exactly those. Every sharing policy maps onto THIS ontology (asserted below).
INFO_KINDS = frozenset({"artifact", "failure", "hypothesis", "observation",
                        "success"})

# evidence provenance classes (H4): what stands behind an observation.
EVIDENCE_CLASSES = ("ENGINE_WORK_RESULT", "CLIENT_ASSERTED")

# world lifecycle transitions that are allowed (fail-closed otherwise)
_WORLD_TRANSITIONS = {
    "CREATED": {"RUNNING", "TERMINATED"},
    "RUNNING": {"PAUSED", "TERMINATED"},
    "PAUSED": {"RUNNING", "TERMINATED"},
    "TERMINATED": set(),
}

# sharing policies (section 13). ISOLATED is the default. A policy names the
# information KINDS that may cross a world boundary via explicit import.
SHARING_POLICIES = {
    "ISOLATED": frozenset(),
    "FAILURES_ONLY": frozenset({"failure"}),
    "HYPOTHESES_ONLY": frozenset({"hypothesis"}),
    "FAILURES_AND_HYPOTHESES": frozenset({"failure", "hypothesis"}),
    "SUCCESSES_ONLY": frozenset({"success"}),         # F2: a first-class kind now
    "FULLY_SHARED": frozenset({"failure", "hypothesis", "artifact",
                              "observation", "success"}),
    "EXPLICIT_IMPORT_ONLY": frozenset({"failure", "hypothesis", "artifact",
                                       "observation", "success"}),
}

# F2 coherence gate (G12): every declared policy must map ONTO the closed
# ontology. This fails at import time if a future edit reintroduces drift.
for _pol, _kinds in SHARING_POLICIES.items():
    assert _kinds <= INFO_KINDS, (
        f"sharing policy {_pol} references kinds outside the info_kind "
        f"ontology: {sorted(_kinds - INFO_KINDS)}")

DEFAULT_LEASE_S = 30.0

# resource enforcement classes (section 12): never fabricate precision.
ENFORCEMENT = ("enforceable", "measured", "estimated", "unavailable")

# ---------------------------------------------------------------------------
# v6 SCIENTIFIC PROVENANCE VOCABULARIES
#
# All closed sets (DFX-4: scientific control configuration fails closed). The
# one deliberate exception is a family's manifest and an experiment's spec,
# which stay freeform because they are the experimenter's own payload.
# ---------------------------------------------------------------------------
SCIENCE_PROFILES = ("off", "warn", "strict")

FAMILY_KINDS = frozenset({"campaign", "analysis", "comparison", "selection"})
FAMILY_MEMBER_KINDS = frozenset({"experiment", "analysis", "world", "claim"})
FAMILY_ROLES = frozenset({"planned", "executed", "abandoned",
                          "selected", "alternative"})

CLAIM_STATUSES = frozenset({"SUPPORTED", "SUCCESSFUL_NEGATIVE",
                            "INCONCLUSIVE", "RETRACTED"})

# COMPOSITIONAL, never an ordinal. Two replication ladders were proposed two
# loops apart on different axes (sequence/terminal/distribution/ranking/
# phenotype, then resampling/world-distribution/landscape/implementation/
# player-build/full). Encoding either as a rank would hard-code a taxonomy that
# has already moved once. Independent booleans survive the taxonomy changing,
# and any ladder anyone prefers is derivable from them.
REPLICATION_DIMENSIONS = frozenset({
    "resampled_noise",      # same world, new draws from the same noise process
    "new_world_draws",      # new worlds from the same generator
    "new_landscape",        # a different problem landscape
    "reimplemented",        # the procedure rewritten independently
    "rebuilt_player",       # the agent/player rebuilt, not merely re-seeded
    "independent_team",     # executed by people who did not run the original
})

# What a declared unit of analysis may be. Counting distinct units under one of
# these keys is COUNTING; it is what separates n=128 from n=8 when 128
# observations come from 8 worlds.
UNITS_OF_ANALYSIS = frozenset({"observation", "experiment", "world",
                               "seed_root", "topology_group"})

# The executed-side attestation columns (v6). The engine already held the
# REQUESTED configuration -- spec_hash, sealed at commit -- and never held the
# executed side, so a run that quietly used a different config was
# indistinguishable from a faithful one.
ATTESTATION_FIELDS = ("executed_config_hash", "entry_state_hash",
                      "player_identity_hash", "measurement_identity_hash")

# Findings that FAIL the call under --science-profile strict. Everything else
# is reported in every non-off profile and blocks in none: a finding blocks
# only when it contradicts a declaration the caller itself sealed.
_STRICT_BLOCKING_CLAIM = frozenset({"CLAIM_CITES_NON_ANALYSIS",
                                    "CLAIM_CITES_UNVERIFIED_ANALYSIS",
                                    "TRANSPORT_OVERREACH"})

# World fields the engine can actually SEE change across a fork. An
# intervention naming anything else is opaque and the engine says nothing --
# silence is the honest answer, not a green light.
_ENGINE_VISIBLE_INTERVENTIONS = ("seed_root", "sharing_policy",
                                 "topology_group")


def _normalize_replication(rep):
    """Validate a compositional replication declaration. Absent is NOT False:
    a dimension the claimant did not mention was not asserted either way, and
    recording it as False would manufacture a negative claim."""
    if rep is None:
        return {}
    if not isinstance(rep, dict):
        raise ValidationError("replication must be an object of "
                              "dimension -> bool",
                              allowed=sorted(REPLICATION_DIMENSIONS))
    unknown = sorted(set(rep) - REPLICATION_DIMENSIONS)
    if unknown:
        raise ValidationError(
            "unknown replication dimension(s); the set is closed on purpose "
            "so that a claim of replication means the same thing to every "
            "reader", unknown=unknown,
            allowed=sorted(REPLICATION_DIMENSIONS))
    bad = sorted(k for k, v in rep.items() if not isinstance(v, bool))
    if bad:
        raise ValidationError("replication dimensions are booleans", bad=bad)
    return {k: v for k, v in sorted(rep.items())}


def _as_set(v):
    if v is None:
        return None
    if isinstance(v, (list, tuple, set)):
        return {json.dumps(x, sort_keys=True) for x in v}
    if isinstance(v, dict):
        return {json.dumps([k, v[k]], sort_keys=True) for k in sorted(v)}
    return {json.dumps(v, sort_keys=True)}


def _transport_findings(transport_domain, analysis_spec) -> list:
    """Is the asserted claim domain wider than the domain actually tested?

    A containment check over two DECLARATIONS. The engine asserts nothing about
    whether a result transports -- it only reports that the claimant said it
    holds somewhere they never tested, which is arithmetic on sets."""
    tested = analysis_spec.get("tested_domain") if isinstance(
        analysis_spec, dict) else None
    t, d = _as_set(transport_domain), _as_set(tested)
    if t is None:
        return []
    if d is None:
        return [{"code": "TRANSPORT_UNCHECKABLE",
                 "message": "a transport_domain was claimed but the cited "
                            "analysis declares no tested_domain, so the "
                            "engine cannot compare them"}]
    excess = sorted(t - d)
    if excess:
        return [{"code": "TRANSPORT_OVERREACH", "excess": excess,
                 "message": "the claimed transport domain includes values the "
                            "cited analysis never tested"}]
    return []


def _analysis_verification_findings(cx, world_id, exp_id) -> list:
    """Did the cited analysis actually resolve its own sources?

    Reads the SEALED ANALYSIS_REGISTERED payload rather than recomputing, for
    the same reason analysis_report does: the verification is a fact recorded
    at registration inside the world's hash chain, not a number regenerated
    later from state that may have moved underneath it."""
    row = cx.execute(
        "SELECT payload FROM events WHERE world_id=? AND "
        "event_type='ANALYSIS_REGISTERED' AND refs LIKE ? "
        "ORDER BY world_index DESC LIMIT 1",
        (world_id, '%"' + exp_id + '"%')).fetchone()
    if row is None:
        return []                    # registered while the profile was off
    try:
        v = json.loads(row["payload"])
    except (TypeError, ValueError):
        return []
    if "verified_n" not in v:        # sealed while the profile was off
        return []
    if v.get("verified_n") == 0 and v.get("sources_submitted"):
        return [{
            "code": "CLAIM_CITES_UNVERIFIED_ANALYSIS",
            "analysis_exp_id": exp_id, "verified_n": 0,
            "sources_submitted": v.get("sources_submitted"),
            "sources_unresolved": v.get("sources_unresolved"),
            "message": "the cited analysis resolved NONE of its sources, so "
                       "this claim rests on an evidentiary base the engine "
                       "recorded as empty"}]
    if v.get("unit_mismatch"):
        return [{
            "code": "CLAIM_CITES_UNVERIFIED_ANALYSIS",
            "analysis_exp_id": exp_id,
            "declared_n": v.get("declared_n"),
            "verified_n": v.get("verified_n"),
            "sources_unresolved": v.get("sources_unresolved"),
            "message": "the cited analysis declared an n the engine's own "
                       "count contradicts"}]
    return []


# v7. What a measured value MEANS. Without direction "0.2 vs 0.4" is not even
# orderable, and an automated analyst that guesses the sign produces a
# confident answer with the wrong one.
MEASUREMENT_DIRECTIONS = frozenset({"HIGHER_IS_BETTER", "LOWER_IS_BETTER",
                                    "NEITHER"})

_PATH_OK = set("abcdefghijklmnopqrstuvwxyz"
               "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-")


def _check_value_path(path) -> None:
    """A dotted path into observations.content. Deliberately not JSONPath: a
    query language would let a measurement SELECT its own value (first match,
    filtered, aggregated), and choosing which of several values counts is the
    interpretation the engine declines to do. A fixed address is a lookup."""
    if not isinstance(path, str) or not path.strip():
        raise ValidationError("value_path must be a non-empty string")
    parts = path.split(".")
    for p in parts:
        if not p or any(c not in _PATH_OK for c in p):
            raise ValidationError(
                "value_path is a dotted path of plain keys, e.g. "
                "'score' or 'metrics.terminal_fitness' -- no wildcards, "
                "filters or indices, because selecting WHICH value counts is "
                "interpretation", value_path=path, bad_segment=p)


def _dig(obj, path: str):
    """Walk a dotted path. Returns (found, value); never raises on a miss,
    because 'the field is absent' is itself a finding an analyst needs."""
    cur = obj
    for p in path.split("."):
        if not isinstance(cur, dict) or p not in cur:
            return False, None
        cur = cur[p]
    return True, cur


def measurement_identity(name, version, implementation_hash, params,
                         value_path) -> str:
    """The canonical identity of a measurement DEFINITION.

    work_items.measurement_identity_hash was a free string: it could detect
    that the scorer changed, but nothing tied it to any definition, so it could
    not say WHAT was measured. Deriving it from the definition makes an
    executor's attestation checkable against a registered measurement instead
    of merely comparable with itself."""
    return content_hash({"name": name, "version": version,
                         "implementation_hash": implementation_hash,
                         "params": params or {}, "value_path": value_path})


def _measurement_dict(r) -> dict:
    return {"measurement_id": r["measurement_id"], "name": r["name"],
            "version": r["version"],
            "implementation_hash": r["implementation_hash"],
            "params": json.loads(r["params"]), "domain": r["domain"],
            "inputs": json.loads(r["inputs"]),
            "outputs": json.loads(r["outputs"]),
            "provenance": json.loads(r["provenance"]),
            "validation_status": r["validation_status"],
            "value_path": r["value_path"], "direction": r["direction"],
            "unit": r["unit"], "range_min": r["range_min"],
            "range_max": r["range_max"],
            "identity_hash": r["identity_hash"],
            "created_ts": r["created_ts"]}


def _grant_dict(r) -> dict:
    return {"grant_id": r["grant_id"], "scope_id": r["scope_id"],
            "grantee_client_id": r["grantee_client_id"],
            "granted_by": r["granted_by"], "note": r["note"],
            "created_ts": r["created_ts"], "revoked_ts": r["revoked_ts"],
            "active": r["revoked_ts"] is None}


def _normalize_attestation(att) -> dict:
    """Accept EITHER the executed config itself (the engine hashes it with the
    same canonicalization that produced spec_hash, so a faithful executor
    matches by construction) OR a precomputed hash for an executor that will
    not disclose its config."""
    if att is None:
        return {}
    if not isinstance(att, dict):
        raise ValidationError("attestation must be an object")
    known = set(ATTESTATION_FIELDS) | {"executed_config"}
    unknown = sorted(set(att) - known)
    if unknown:
        raise ValidationError("unknown attestation field(s)", unknown=unknown,
                              allowed=sorted(known))
    if "executed_config" in att and "executed_config_hash" in att:
        raise ValidationError(
            "send executed_config OR executed_config_hash, not both: two "
            "sources for one fact is exactly the ambiguity this closes")
    out = {}
    if "executed_config" in att:
        out["executed_config_hash"] = content_hash(att["executed_config"])
    for f in ATTESTATION_FIELDS:
        if f in att:
            v = att[f]
            if not isinstance(v, str) or not v.strip():
                raise ValidationError("attestation values are non-empty "
                                      "strings", field=f)
            out[f] = v
    return out


def _intervention_findings(parent_row, child_spec, child_values) -> list:
    """Everything the engine can say about whether an intervention did anything.

    Interventions were recorded VERBATIM in WORLD_FORKED and nowhere else, so a
    perturbation that changed nothing was indistinguishable from one that
    worked -- a mistake that has actually been made and caught by hand. Two
    deterministic tests, no statistics:

      1. a DECLARED before/after pair whose content hashes are equal;
      2. every engine-visible field the intervention names either already
         holding the parent's value in the child, or not carrying the value the
         intervention declared at all.

    THE TWO ARE INDEPENDENT EVIDENCE AND BOTH ALWAYS RUN. Until 2026-09-06 this
    function returned at most ONE finding, and the declared-before/after branch
    returned early: a differing pair meant the engine-visible checks were never
    reached. So a fork declaring `interventions: {"seed_root": 99}` together
    with any non-identical before/after pair produced NO finding at all, even
    though the child's seed_root was still the parent's.

    The incentive that created was exactly backwards. Supplying
    intervention_effect is the more informative, more conscientious thing to
    do, and doing it silently disarmed the stronger check -- the careless
    caller who omitted it got INTERVENTION_NOT_APPLIED, the careful one got
    silence. A check that punishes disclosure is worse than no check.

    A DIFFERING before/after pair is NOT evidence that the intervention was
    applied. It is the claimant's own account of two states; the engine-visible
    comparison is the engine's. They can disagree, and when they do that
    disagreement is the finding worth having.

    Where an intervention names something the engine cannot see, the engine
    still returns nothing rather than a reassurance it has not earned."""
    iv = child_spec.get("interventions") or {}
    if not isinstance(iv, dict) or not iv:
        return []
    out = []

    # (1) the claimant's declared account of the effect
    eff = child_spec.get("intervention_effect")
    if isinstance(eff, dict) and "before" in eff and "after" in eff:
        bh, ah = content_hash(eff["before"]), content_hash(eff["after"])
        if bh == ah:
            out.append({"code": "NO_EFFECTIVE_INTERVENTION",
                        "basis": "declared_before_after",
                        "before_hash": bh, "after_hash": ah,
                        "message": "the declared before/after states are "
                                   "byte-identical: this intervention changed "
                                   "nothing"})
        # a DIFFERING pair proves nothing about the fields below -- fall through

    # (2) what the engine can see for itself, ALWAYS
    visible = [k for k in _ENGINE_VISIBLE_INTERVENTIONS if k in iv]
    if not visible:
        return out
    not_applied = [k for k in visible if child_values.get(k) != iv[k]]
    if not_applied:
        out.append({"code": "INTERVENTION_NOT_APPLIED", "fields": not_applied,
                    "message": "the intervention declares a value the forked "
                               "child does not actually carry"})
        return out
    inert = [k for k in visible if child_values.get(k) == parent_row[k]]
    if inert and len(visible) == len(iv):
        if len(inert) == len(visible):
            out.append({"code": "NO_EFFECTIVE_INTERVENTION",
                        "basis": "engine_visible_fields", "fields": inert,
                        "message": "every field this intervention names "
                                   "already holds the parent's value in the "
                                   "child"})
        else:
            out.append({"code": "PARTIALLY_INERT_INTERVENTION",
                        "fields": inert,
                        "message": "some fields this intervention names "
                                   "already hold the parent's value in the "
                                   "child"})
    return out


# Findings that CONTRADICT a declaration the forking caller sealed in the same
# request. Both fail the call under strict, and under any profile when the
# child asserts intervention_effective. PARTIALLY_INERT_INTERVENTION is
# deliberately NOT here: a partly-inert intervention is informative, not
# self-contradictory.
_FORK_CONTRADICTIONS = frozenset({"NO_EFFECTIVE_INTERVENTION",
                                  "INTERVENTION_NOT_APPLIED"})


class Foundry:
    def __init__(self, db_path: str, *, science_profile: str = "warn"):
        """science_profile grades the v6 provenance checks: off | warn | strict.

        It defaults to "warn" because a check nobody sees is a check nobody
        acts on, and warn cannot break a caller -- it only adds keys. "off" is
        a genuine control arm: the checks are not computed at all, so an
        off/warn A/B measures the feature rather than two different engines."""
        if science_profile not in SCIENCE_PROFILES:
            raise ValueError("science_profile must be one of %s"
                             % (SCIENCE_PROFILES,))
        self.science_profile = science_profile
        self.store = Store(db_path)
        self.store.initialize()

    def close(self) -> None:
        self.store.close()

    # ================= identity =========================================
    def create_client(self, name: str, token_hash: Optional[str] = None) -> str:
        cid = new_id("client")
        with self.store.write() as cx:
            cx.execute("INSERT INTO clients(client_id,name,token_hash,created_ts)"
                       " VALUES(?,?,?,?)", (cid, name, token_hash, now()))
            events.append_foundry(cx, "CLIENT_CREATED", actor=cid,
                                  scope_kind="client", scope_id=cid,
                                  payload={"name": name})
        return cid

    def open_session(self, client_id: str, name: str) -> dict:
        """Open a session and mint its AFFINITY KEY.

        The key is bearer-like: returned once, stored only as a SHA-256, and
        never logged whole. Its plaintext deliberately CARRIES this engine's
        instance id, because that is what makes a wrong-engine request
        distinguishable from noise: an engine that receives a key minted
        elsewhere can read the instance id out of the key itself and answer
        WRONG_SESSION without any database lookup. If the id were only in the
        database, a foreign key and a random string would be the same event --
        an absent row -- and the engine could not tell "you are talking to the
        wrong machine" from "that session never existed", which is the exact
        confusion this feature exists to end.

        The instance id is not a secret. It is already published by
        verify_anchor and the audit envelope to any holder of an anchor. The
        secret is the random tail."""
        sid = new_id("session")
        iid = self.engine_instance_id()
        key = session_key_for(iid)
        with self.store.write() as cx:
            if cx.execute("SELECT 1 FROM clients WHERE client_id=?",
                          (client_id,)).fetchone() is None:
                raise NotFound("unknown client", client_id=client_id)
            cx.execute("INSERT INTO sessions(session_id,client_id,name,"
                       "created_ts,key_hash,engine_instance_id,affinity_mode)"
                       " VALUES(?,?,?,?,?,?,'STRICT')",
                       (sid, client_id, name, now(), _sha(key), iid))
            events.append_foundry(cx, "SESSION_CREATED", actor=client_id,
                                  scope_kind="session", scope_id=sid,
                                  payload={"name": name, "client_id": client_id,
                                           "engine_instance_id": iid,
                                           "affinity_mode": "STRICT",
                                           "session_key_fp": key_fingerprint(key)})
        return {"session_id": sid, "session_key": key,
                "engine_instance_id": iid, "affinity_mode": "STRICT",
                "note": "session_key shown once; send it as X-SFE-Session on "
                        "every experiment-scoped call"}

    def create_session(self, client_id: str, name: str) -> str:
        """Backwards-compatible: returns ONLY the session id.

        open_session() returns the affinity key as well. This wrapper is kept
        because the session key is a NEW capability and changing an existing
        method's return type breaks every caller silently -- which it did:
        117 tests failed with a dict being bound as a SQL parameter before this
        was split back apart."""
        return self.open_session(client_id, name)["session_id"]

    def close_session(self, session_id: str, *,
                      client_id: Optional[str] = None) -> dict:
        """End a session's lifecycle. Idempotent.

        HARMONIA 2026-09-05 found two consequences of this not existing, and
        they are the same gap seen from two sides:
          * SESSION_CLOSED (409) was in the error taxonomy but UNREACHABLE --
            a documented failure no client could ever trigger or test.
          * the strict-cutover drain condition (sessions_legacy_open == 0) could
            never move, because nothing closes a session. The cutover was
            date-driven by accident rather than by decision.

        Gated on OWNERSHIP (the bearer token), NOT on the session key. That is
        deliberate: the 106 LEGACY sessions never had a key, so a key-gated
        close would leave exactly the sessions that need draining permanently
        undrainable.

        Closing does NOT terminate or delete worlds and does not touch their
        events. It ends the session: the key stops authenticating (409), and no
        new world can be created under it."""
        with self.store.write() as cx:
            row = cx.execute("SELECT client_id, state, affinity_mode FROM "
                             "sessions WHERE session_id=?",
                             (session_id,)).fetchone()
            if row is None:
                raise NotFound("unknown session", session_id=session_id)
            if client_id is not None and row["client_id"] != client_id:
                raise AccessDenied("session not owned by this client",
                                   session_id=session_id)
            if row["state"] == "CLOSED":
                return {"session_id": session_id, "state": "CLOSED",
                        "already_closed": True}
            cx.execute("UPDATE sessions SET state='CLOSED' WHERE session_id=?",
                       (session_id,))
            events.append_foundry(cx, "SESSION_CLOSED", actor=row["client_id"],
                                  scope_kind="session", scope_id=session_id,
                                  payload={"affinity_mode": row["affinity_mode"]})
            return {"session_id": session_id, "state": "CLOSED",
                    "already_closed": False}

    # ---- session affinity -------------------------------------------------
    def resolve_session(self, key: Optional[str]) -> dict:
        """Classify a presented session key WITHOUT touching any resource.

        Returns {"status": ..., ...}. Never raises: the caller decides the HTTP
        mapping, because 'missing' is legal for a LEGACY session and fatal for
        a strict one, and only the caller knows which route it is on.

        Order matters and is deliberate: the wrong-engine test is made from the
        key's own bytes BEFORE any lookup, so a foreign key is never merely
        'not found'."""
        if key is None or key == "":
            return {"status": "MISSING"}
        iid = self.engine_instance_id()
        claimed = engine_id_from_key(key)
        if claimed is None:
            return {"status": "MALFORMED"}
        if claimed != iid:
            # THE headline case. Answered from the key alone -- no lookup, so
            # it cannot be confused with a missing resource, and it is decided
            # identically whether or not the far engine is reachable.
            return {"status": "WRONG_ENGINE", "claimed_engine": claimed,
                    "this_engine": iid}
        row = self.store.read().execute(
            "SELECT session_id, client_id, state, affinity_mode "
            "FROM sessions WHERE key_hash=?", (_sha(key),)).fetchone()
        if row is None:
            # Well-formed, names THIS engine, but no such session: a restore
            # from a different backup, or a revoked/pruned session.
            return {"status": "UNKNOWN"}
        if row["state"] != "OPEN":
            return {"status": "CLOSED", "session_id": row["session_id"]}
        return {"status": "OK", "session_id": row["session_id"],
                "client_id": row["client_id"],
                "affinity_mode": row["affinity_mode"]}

    def session_affinity_mode(self, session_id: str) -> Optional[str]:
        row = self.store.read().execute(
            "SELECT affinity_mode FROM sessions WHERE session_id=?",
            (session_id,)).fetchone()
        return row["affinity_mode"] if row else None

    def world_session_id(self, world_id: str) -> Optional[str]:
        row = self.store.read().execute(
            "SELECT session_id FROM worlds WHERE world_id=?",
            (world_id,)).fetchone()
        return row["session_id"] if row else None

    def affinity_census(self) -> dict:
        """Operator/roadmap signal: how far the LEGACY tail has drained. The
        strict-mode cutover is defined against these numbers, not a feeling."""
        cx = self.store.read()
        one = lambda q: cx.execute(q).fetchone()[0]      # noqa: E731
        return {
            "engine_instance_id": self.engine_instance_id(),
            "sessions_total": one("SELECT COUNT(*) FROM sessions"),
            "sessions_strict":
                one("SELECT COUNT(*) FROM sessions WHERE affinity_mode='STRICT'"),
            "sessions_legacy":
                one("SELECT COUNT(*) FROM sessions WHERE affinity_mode='LEGACY'"),
            "sessions_legacy_open":
                one("SELECT COUNT(*) FROM sessions WHERE affinity_mode='LEGACY'"
                    " AND state='OPEN'"),
            "worlds_on_legacy_sessions":
                one("SELECT COUNT(*) FROM worlds w JOIN sessions s"
                    " ON s.session_id=w.session_id"
                    " WHERE s.affinity_mode='LEGACY'"),
        }

    def revoke_token(self, client_id: str) -> None:
        """Operator-controlled revocation: the client's current token stops
        authenticating immediately (its stored hash is cleared, so no bearer
        token can resolve to this client until one is reissued). The client
        IDENTITY -- and every provenance record bound to it -- is unchanged."""
        with self.store.write() as cx:
            if cx.execute("SELECT 1 FROM clients WHERE client_id=?",
                          (client_id,)).fetchone() is None:
                raise NotFound("unknown client", client_id=client_id)
            cx.execute("UPDATE clients SET token_hash=NULL WHERE client_id=?",
                       (client_id,))
            events.append_foundry(cx, "CLIENT_TOKEN_REVOKED", actor="operator",
                                  scope_kind="client", scope_id=client_id,
                                  payload={})

    def reissue_token(self, client_id: str, token_hash: str) -> None:
        """Operator-controlled rotation: bind a NEW token to the SAME client
        identity. The old token (any prior hash) stays dead; history and
        provenance remain bound to the unchanged client_id."""
        with self.store.write() as cx:
            if cx.execute("SELECT 1 FROM clients WHERE client_id=?",
                          (client_id,)).fetchone() is None:
                raise NotFound("unknown client", client_id=client_id)
            cx.execute("UPDATE clients SET token_hash=? WHERE client_id=?",
                       (token_hash, client_id))
            events.append_foundry(cx, "CLIENT_TOKEN_REISSUED", actor="operator",
                                  scope_kind="client", scope_id=client_id,
                                  payload={})

    def create_topology_group(self, client_id: str, *,
                              note: Optional[str] = None) -> str:
        """Mint a REGISTERED sharing group (H5). The returned id is a server-
        issued unguessable capability: cross-client sharing works only when
        both worlds carry this id, which two clients can share only by
        deliberate out-of-band transfer -- string-guessing can never
        manufacture bilateral consent."""
        gid = new_id("group")
        with self.store.write() as cx:
            if cx.execute("SELECT 1 FROM clients WHERE client_id=?",
                          (client_id,)).fetchone() is None:
                raise NotFound("unknown client", client_id=client_id)
            cx.execute("INSERT INTO topology_groups(group_id,created_by,note,"
                       "created_ts) VALUES(?,?,?,?)",
                       (gid, client_id, note, now()))
            events.append_foundry(cx, "TOPOLOGY_GROUP_CREATED", actor=client_id,
                                  scope_kind="group", scope_id=gid, payload={})
        return gid

    # ================= idempotency (F5) =================================
    def _idem_check(self, cx, client_id, key, request_hash):
        """Inside the caller's write txn: if this (client, key) already completed
        with the SAME semantic request, return its stored response for replay; a
        DIFFERENT request under the same key is a conflict; a first use returns
        None. The caller MUST call _idem_record before the txn commits, so key +
        response + epistemic object commit ATOMICALLY -- exactly-once holds even
        across a process restart mid-retry (either all committed or none did).
        Scope is (client_id, key); request_hash binds route+world+body, so a key
        reused for another world is a conflict, never a cross-world dedup."""
        if key is None:
            return None
        row = cx.execute(
            "SELECT request_hash, response, route, world_id FROM "
            "idempotency_keys WHERE client_id=? AND idem_key=?",
            (client_id, key)).fetchone()
        if row is None:
            return None
        if row["request_hash"] != request_hash:
            # Say WHAT differed. request_hash binds route + world + body, and
            # by far the most common cause is a key that is unique per logical
            # step but NOT per world -- reused across worlds it conflicts on
            # every world after the first, which reads as a random scatter of
            # 409s. Naming the first-use route and world turns that into an
            # obvious diagnosis.
            raise ConflictError(
                "idempotency key reused for a materially different request; "
                "the key is scoped to (client, key) and the request hash binds "
                "route + world_id + body, so a key reused for a different world "
                "conflicts rather than de-duplicating. Make the key unique per "
                "(world, step).",
                idem_key=key, first_used_route=row["route"],
                first_used_world_id=row["world_id"])
        return json.loads(row["response"])

    def _idem_record(self, cx, client_id, key, world_id, route, request_hash,
                     response):
        if key is None:
            return
        cx.execute(
            "INSERT INTO idempotency_keys(client_id,idem_key,world_id,route,"
            "request_hash,response,created_ts) VALUES(?,?,?,?,?,?,?)",
            (client_id, key, world_id, route, request_hash,
             json.dumps(response), now()))

    # ================= world lifecycle ==================================
    def create_world(self, session_id: str, name: str, *,
                     sharing_policy: str = "ISOLATED",
                     seed_root: Optional[int] = None,
                     topology_group: Optional[str] = None,
                     budget: Optional[dict] = None,
                     require_attestation: bool = False,
                     idem_key: Optional[str] = None,
                     request_hash: Optional[str] = None) -> dict:
        """Create a world.

        RETRY SAFETY (D-IDEM-1, 2026-09-04): pass idem_key to make creation
        retry-safe. Without one, world creation is UNSAFE TO RETRY BLINDLY --
        the config is NOT the identity, so an orchestrator that retries after a
        timeout mints a SECOND CAUSAL UNIVERSE and both halves of the
        experiment look real. With a key, a repeat of the SAME semantic request
        replays the first world; a DIFFERENT request under that key is a
        diagnosable 409 conflict, never a silent second world.

        The key + the world row + the WORLD_CREATED event commit in ONE
        transaction, so a crash mid-retry leaves either both or neither -- the
        same exactly-once property the other epistemic writes already have."""
        if sharing_policy not in SHARING_POLICIES:
            raise ValidationError("unknown sharing policy",
                                  sharing_policy=sharing_policy,
                                  allowed=sorted(SHARING_POLICIES))
        wid = new_id("world")
        if seed_root is None:
            # NOTE: a caller relying on idempotency MUST pass an explicit
            # seed_root. A server-minted seed differs per call, so it is
            # deliberately excluded from the caller's request_hash (which is
            # computed from the REQUEST body upstream) -- the replay returns
            # the FIRST world, seed included, which is the retry-safe answer.
            seed_root = random.SystemRandom().randrange(1 << 62)
        with self.store.write() as cx:
            s = cx.execute("SELECT client_id FROM sessions WHERE session_id=? "
                           "AND state='OPEN'", (session_id,)).fetchone()
            if s is None:
                raise NotFound("unknown or closed session",
                               session_id=session_id)
            cid = s["client_id"]
            replay = self._idem_check(cx, cid, idem_key, request_hash)
            if replay is not None:
                return replay
            cx.execute(
                "INSERT INTO worlds(world_id,session_id,client_id,name,state,"
                "sharing_policy,topology_group,seed_root,budget_root,"
                "require_attestation,created_ts) "
                "VALUES(?,?,?,?,'CREATED',?,?,?,?,?,?)",
                (wid, session_id, cid, name, sharing_policy, topology_group,
                 int(seed_root), wid, 1 if require_attestation else 0, now()))
            self._init_budget(cx, wid, budget or {})
            events.append(cx, wid, "WORLD_CREATED", actor=cid, payload={
                "name": name, "sharing_policy": sharing_policy,
                "topology_group": topology_group, "seed_root": int(seed_root),
                "require_attestation": bool(require_attestation),
                "session_id": session_id})
            out = _world_dict(self._world_row(cx, wid))
            self._idem_record(cx, cid, idem_key, wid, "worlds", request_hash,
                              out)
            return out

    def _world_row(self, cx, world_id: str):
        r = cx.execute("SELECT * FROM worlds WHERE world_id=?",
                       (world_id,)).fetchone()
        if r is None:
            raise NotFound("unknown world", world_id=world_id)
        return r

    def _authorize_write(self, cx, world_id: str, client_id: Optional[str]):
        """Ownership check PLUS the terminal-state gate (D-LIFECYCLE-1).

        TERMINATED is a TERMINAL state and ends the world's scientific write
        lifetime. Before 2026-09-04 it ended only STATE TRANSITIONS and work
        ENQUEUE: artifacts, hypotheses, budget debits and fresh work claims all
        still succeeded afterwards (Harmonia B4, and it generalized further than
        artifacts when measured). That made "terminated" mean nothing a fossil
        could rely on -- the head hash at termination was not final, so a replay
        could not trust that it had the whole world.

        What is STILL permitted after termination, deliberately and typed:
          * every read (events, history, status, artifact content, knowledge)
          * checkpoint  -- snapshots already-final state; appends no science
          * fork        -- the CHILD is a new world; replay, counterfactual and
                           fixed-world rerun all depend on forking a FINISHED
                           world, so forbidding this would break the experiment
                           designs the engine exists to serve
          * complete_work / fail_work for work claimed BEFORE termination --
            in-flight settlement. Refusing would strand the lease forever and
            force the ledger to misreport what the worker actually did.
        """
        r = self._authorize(cx, world_id, client_id)
        if r["state"] == "TERMINATED":
            raise InvalidTransition(
                "world is TERMINATED; its scientific write lifetime has ended. "
                "Reads, checkpoint and fork still work -- fork the world if you "
                "need to continue or vary the run.",
                world_id=world_id, state="TERMINATED")
        return r

    def _authorize(self, cx, world_id: str, client_id: Optional[str]):
        """Ownership check (I5, T8). A client may only touch its own worlds.
        `client_id=None` is an internal/system call (executors) and is allowed;
        the API layer always passes a concrete client id."""
        r = self._world_row(cx, world_id)
        if client_id is not None and r["client_id"] != client_id:
            # do NOT leak existence details beyond "denied"
            raise AccessDenied("world is not owned by this client",
                               world_id=world_id)
        return r

    def get_world(self, world_id: str, client_id: Optional[str] = None) -> dict:
        """The world's FULL configuration.

        B5 (Harmonia, 2026-09-04): `budget` used to be absent here, so a fossil
        could not record the world configuration it ran under without a second
        call to /resources -- and the replay analysis scored world_configuration
        AMBIGUOUS for exactly that reason. The enforcement limits are part of
        the world's identity for replay, so they are returned with it."""
        cx = self.store.read()
        r = self._authorize(cx, world_id, client_id)
        out = _world_dict(r)
        out["budget"] = self._budget_config(cx, world_id)
        return out

    def _transition(self, world_id: str, client_id: Optional[str], target: str,
                    event_type: str, payload: Optional[dict] = None) -> dict:
        with self.store.write() as cx:
            r = self._authorize(cx, world_id, client_id)
            cur = r["state"]
            if target not in _WORLD_TRANSITIONS[cur]:
                raise InvalidTransition(
                    f"cannot go {cur} -> {target}", world_id=world_id,
                    current=cur, target=target)
            extra = ""
            args = [target]
            if target == "TERMINATED":
                extra = ", terminated_ts=?"
                args.append(now())
            args.append(world_id)
            cx.execute(f"UPDATE worlds SET state=?{extra} WHERE world_id=?",
                       tuple(args))
            events.append(cx, world_id, event_type,
                          actor=r["client_id"], payload=payload or {})
            return _world_dict(self._world_row(cx, world_id))

    def start_world(self, world_id, client_id=None):
        return self._transition(world_id, client_id, "RUNNING", "WORLD_STARTED")

    def pause_world(self, world_id, client_id=None):
        return self._transition(world_id, client_id, "PAUSED", "WORLD_PAUSED")

    def resume_world(self, world_id, client_id=None):
        return self._transition(world_id, client_id, "RUNNING", "WORLD_RESUMED")

    def terminate_world(self, world_id, client_id=None):
        return self._transition(world_id, client_id, "TERMINATED",
                                "WORLD_TERMINATED")

    def list_worlds(self, *, session_id=None, client_id=None, state=None,
                    created_after=None, created_before=None) -> list:
        """Enumerate worlds, always scoped to the caller when client_id is given.

        The optional filters answer the four questions an orchestrator actually
        has -- which worlds are mine, which are active, which are finished,
        which are cleanup candidates -- without becoming a search engine."""
        if state is not None and state not in _WORLD_TRANSITIONS:
            raise ValidationError("unknown world state", state=state,
                                  allowed=sorted(_WORLD_TRANSITIONS))
        cx = self.store.read()
        q, a = "SELECT * FROM worlds WHERE 1=1", []
        if session_id:
            q += " AND session_id=?"; a.append(session_id)
        if client_id:
            q += " AND client_id=?"; a.append(client_id)
        if state:
            q += " AND state=?"; a.append(state)
        if created_after is not None:
            q += " AND created_ts>?"; a.append(float(created_after))
        if created_before is not None:
            q += " AND created_ts<?"; a.append(float(created_before))
        q += " ORDER BY created_ts"
        return [_world_dict(r) for r in cx.execute(q, tuple(a)).fetchall()]

    # ================= work queue =======================================
    def enqueue_work(self, world_id: str, kind: str, payload: dict, *,
                     client_id: Optional[str] = None, priority: int = 100,
                     max_attempts: int = 3,
                     dedup_key: Optional[str] = None) -> str:
        wkid = new_id("work")
        with self.store.write() as cx:
            r = self._authorize(cx, world_id, client_id)
            if r["state"] == "TERMINATED":
                raise InvalidTransition("cannot enqueue into a terminated world",
                                        world_id=world_id)
            try:
                cx.execute(
                    "INSERT INTO work_items(work_id,world_id,kind,payload,"
                    "priority,max_attempts,dedup_key,created_ts,updated_ts) "
                    "VALUES(?,?,?,?,?,?,?,?,?)",
                    (wkid, world_id, kind, json.dumps(payload), priority,
                     max_attempts, dedup_key, now(), now()))
            except Exception as e:
                if "UNIQUE" in str(e) and dedup_key is not None:
                    ex = cx.execute("SELECT work_id FROM work_items WHERE "
                                    "world_id=? AND dedup_key=?",
                                    (world_id, dedup_key)).fetchone()
                    return ex["work_id"]     # idempotent enqueue
                raise
            events.append(cx, world_id, "WORK_ENQUEUED", actor=r["client_id"],
                          refs={"work_id": wkid}, payload={"kind": kind})
        return wkid

    def _reclaim_expired(self, cx) -> int:
        """Move leases that expired back to RETRYABLE (or EXPIRED if out of
        attempts). Called under the write lock at claim time so a dead worker's
        work is recovered without a background sweeper (I3, T5)."""
        t = now()
        rows = cx.execute(
            "SELECT work_id, world_id, attempts, max_attempts FROM work_items "
            "WHERE status IN ('CLAIMED','RUNNING') AND lease_expires < ?",
            (t,)).fetchall()
        for r in rows:
            newst = "RETRYABLE" if r["attempts"] < r["max_attempts"] else "EXPIRED"
            # claim_id is CLEARED on reclaim (H1): the old attempt's fencing
            # token becomes permanently stale, so a delayed result from the
            # expired attempt can never complete the current one -- even from
            # the SAME worker_id.
            cx.execute("UPDATE work_items SET status=?, claimed_by=NULL, "
                       "claim_id=NULL, lease_expires=NULL, updated_ts=? "
                       "WHERE work_id=?",
                       (newst, t, r["work_id"]))
            events.append(cx, r["world_id"], "WORK_EXPIRED",
                          actor="foundry", refs={"work_id": r["work_id"]},
                          payload={"reclaimed_as": newst})
        return len(rows)

    def claim_work(self, worker_id: str, *, world_id: Optional[str] = None,
                   client_id: Optional[str] = None,
                   lease_s: float = DEFAULT_LEASE_S) -> Optional[dict]:
        """Atomically claim one claimable work item. Under BEGIN IMMEDIATE the
        select-then-update is exclusive, so two workers never claim the same
        unit (I3, T7). Paused/terminated worlds are skipped (a paused world must
        not consume execution resources, section 4).

        `client_id` scopes the claim to that client's OWN worlds (experimenter
        isolation, I5): an unscoped claim (world_id=None) by an experimenter
        never reaches another experimenter's queue -- it cannot even observe a
        foreign work item's payload, let alone hold a lease on it. client_id=None
        is an internal/system worker and applies no tenant filter (mirrors the
        _authorize convention)."""
        with self.store.write() as cx:
            self._reclaim_expired(cx)
            q = ("SELECT w.work_id, w.world_id FROM work_items w "
                 "JOIN worlds d ON d.world_id=w.world_id "
                 "WHERE w.status IN ('QUEUED','RETRYABLE') "
                 "AND d.state='RUNNING' ")
            a: list = []
            if client_id is not None:
                q += "AND d.client_id=? "; a.append(client_id)
            if world_id is not None:
                q += "AND w.world_id=? "; a.append(world_id)
            q += "ORDER BY w.priority ASC, w.created_ts ASC LIMIT 1"
            cand = cx.execute(q, tuple(a)).fetchone()
            if cand is None:
                return None
            t = now()
            # server-issued FENCING token for THIS claim attempt (H1). It is
            # required on heartbeat/complete/fail and is invalidated on reclaim,
            # so an expired attempt's result can never become authoritative.
            claim_id = new_id("claim")
            cx.execute(
                "UPDATE work_items SET status='CLAIMED', claimed_by=?, "
                "claim_id=?, lease_expires=?, heartbeat_ts=?, "
                "attempts=attempts+1, updated_ts=? WHERE work_id=? AND "
                "status IN ('QUEUED','RETRYABLE')",
                (worker_id, claim_id, t + lease_s, t, t, cand["work_id"]))
            events.append(cx, cand["world_id"], "WORK_CLAIMED", actor=worker_id,
                          refs={"work_id": cand["work_id"],
                                "claim_id": claim_id})
            row = cx.execute("SELECT * FROM work_items WHERE work_id=?",
                             (cand["work_id"],)).fetchone()
            return _work_dict(row)

    def start_work(self, work_id: str, worker_id: str, *,
                   claim_id: Optional[str] = None,
                   client_id: Optional[str] = None) -> dict:
        with self.store.write() as cx:
            r = self._owned_claim(cx, work_id, worker_id, {"CLAIMED"},
                                  client_id=client_id, claim_id=claim_id)
            cx.execute("UPDATE work_items SET status='RUNNING', updated_ts=? "
                       "WHERE work_id=?", (now(), work_id))
            events.append(cx, r["world_id"], "WORK_STARTED", actor=worker_id,
                          refs={"work_id": work_id})
            return _work_dict(cx.execute("SELECT * FROM work_items WHERE "
                                         "work_id=?", (work_id,)).fetchone())

    def heartbeat(self, work_id: str, worker_id: str,
                  lease_s: float = DEFAULT_LEASE_S, *,
                  claim_id: Optional[str] = None,
                  client_id: Optional[str] = None) -> dict:
        with self.store.write() as cx:
            r = self._owned_claim(cx, work_id, worker_id, {"CLAIMED", "RUNNING"},
                                  client_id=client_id, claim_id=claim_id)
            t = now()
            cx.execute("UPDATE work_items SET lease_expires=?, heartbeat_ts=?, "
                       "updated_ts=? WHERE work_id=?",
                       (t + lease_s, t, t, work_id))
            events.append(cx, r["world_id"], "WORK_HEARTBEAT", actor=worker_id,
                          refs={"work_id": work_id})
            return {"work_id": work_id, "lease_expires": t + lease_s}

    def _owned_claim(self, cx, work_id, worker_id, allowed_states,
                     client_id=None, claim_id=None):
        r = cx.execute("SELECT * FROM work_items WHERE work_id=?",
                       (work_id,)).fetchone()
        if r is None:
            raise NotFound("unknown work item", work_id=work_id)
        # defense-in-depth (I5): the work item's world must belong to the caller.
        # client_id=None is an internal/system worker (mirrors _authorize).
        if client_id is not None:
            self._authorize(cx, r["world_id"], client_id)
        # H1 lease fencing: the caller must present the server-issued token of
        # the CURRENT claim attempt. worker_id alone is caller-supplied and is
        # NOT sufficient identity; a reclaim clears claim_id, so a stale attempt
        # (even from the same worker_id) can never act on the current one.
        if claim_id is None:
            raise ConflictError(
                "claim_id (the fencing token issued at claim) is required",
                work_id=work_id)
        if (r["status"] not in allowed_states or r["claimed_by"] != worker_id
                or r["claim_id"] != claim_id):
            raise ConflictError(
                "work not held under this claim attempt (stale lease, foreign "
                "worker, or disallowed state)",
                work_id=work_id, status=r["status"], claimed_by=r["claimed_by"],
                worker_id=worker_id)
        return r

    def complete_work(self, work_id: str, worker_id: str, result: dict, *,
                      claim_id: Optional[str] = None,
                      client_id: Optional[str] = None,
                      attestation: Optional[dict] = None) -> dict:
        """Idempotent, exactly-once completion (I3, T7). If already completed
        under THIS claim attempt, the stored result is returned; any other
        attempt -- a distinct worker, or a STALE lease whose claim_id was
        invalidated by reclaim (H1) -- is rejected. Exactly one authoritative
        result, provably from the current claim attempt."""
        with self.store.write() as cx:
            r = cx.execute("SELECT * FROM work_items WHERE work_id=?",
                           (work_id,)).fetchone()
            if r is None:
                raise NotFound("unknown work item", work_id=work_id)
            if client_id is not None:                 # defense-in-depth (I5)
                self._authorize(cx, r["world_id"], client_id)
            if claim_id is None:                      # H1: fencing is mandatory
                raise ConflictError(
                    "claim_id (the fencing token issued at claim) is required",
                    work_id=work_id)
            if r["status"] == "COMPLETED":
                if r["claimed_by"] == worker_id and r["claim_id"] == claim_id:
                    # HARMONIA 2026-09-05, T2 case C3e. A replay of the SAME
                    # result is idempotent and returns the stored row. A replay
                    # carrying a DIFFERENT result used to return 200 with the
                    # ORIGINAL result, so a caller that did not compare
                    # result_hash could believe its second result had been
                    # recorded. Nothing was ever overwritten -- the defect was
                    # the DIAGNOSIS, and a silent 200 for a materially
                    # different request contradicts the engine's own
                    # idempotency rule everywhere else ("same key + a different
                    # request is a 409 conflict").
                    incoming = content_hash(result)
                    if r["result_hash"] is not None and \
                            incoming != r["result_hash"]:
                        raise ConflictError(
                            "this work item is already COMPLETED with a "
                            "DIFFERENT result; the stored result is "
                            "authoritative and was not replaced",
                            work_id=work_id, stored_result_hash=r["result_hash"],
                            submitted_result_hash=incoming)
                    att_r = _normalize_attestation(attestation)
                    ech = att_r.get("executed_config_hash")
                    if ech is not None and r["executed_config_hash"] \
                            is not None and ech != r["executed_config_hash"]:
                        raise ConflictError(
                            "this work item is already COMPLETED under a "
                            "DIFFERENT executed-config attestation; the stored "
                            "attestation is authoritative and was not replaced",
                            work_id=work_id,
                            stored_executed_config_hash=r[
                                "executed_config_hash"],
                            submitted_executed_config_hash=ech)
                    return _work_dict(r)          # idempotent replay
                raise ConflictError("work already completed by another claim "
                                    "attempt", work_id=work_id,
                                    claimed_by=r["claimed_by"])
            if (r["claimed_by"] != worker_id or r["claim_id"] != claim_id
                    or r["status"] not in ("CLAIMED", "RUNNING")):
                raise ConflictError(
                    "cannot complete: not held under this claim attempt "
                    "(stale lease after reclaim, foreign worker, or "
                    "disallowed state)",
                    work_id=work_id, status=r["status"],
                    claimed_by=r["claimed_by"])
            rhash = content_hash(result)
            att = _normalize_attestation(attestation)
            # v6: the engine has always held the REQUESTED configuration --
            # spec_hash, sealed at commit and order-proved by committed_seq. It
            # never held the EXECUTED side, so a worker that ran a different
            # config returned a result the ledger could not distinguish from a
            # faithful one. Comparing two hashes closes that; the engine
            # understands none of the parameters involved.
            ex = cx.execute("SELECT exp_id, spec_hash FROM experiments "
                            "WHERE work_id=?", (work_id,)).fetchone()
            finding = None
            if self.science_profile != "off" and ex is not None:
                ech = att.get("executed_config_hash")
                if ech is None:
                    finding = {"code": "NO_EXECUTION_ATTESTATION",
                               "exp_id": ex["exp_id"],
                               "requested_config_hash": ex["spec_hash"],
                               "message": "the result carries no executed-"
                                          "config attestation, so it cannot be "
                                          "checked against the sealed spec"}
                elif ech != ex["spec_hash"]:
                    finding = {"code": "CONFIG_DIVERGENCE",
                               "exp_id": ex["exp_id"],
                               "requested_config_hash": ex["spec_hash"],
                               "executed_config_hash": ech,
                               "message": "the executor attests to a "
                                          "configuration that is not the one "
                                          "sealed at commit"}
                if self.science_profile == "strict" and finding is not None:
                    raise ConflictError(
                        "science-profile=strict: " + finding["message"],
                        work_id=work_id, **{k: v for k, v in finding.items()
                                            if k != "message"})
            cx.execute("UPDATE work_items SET status='COMPLETED', result=?, "
                       "result_hash=?, executed_config_hash=?, "
                       "entry_state_hash=?, player_identity_hash=?, "
                       "measurement_identity_hash=?, completed_ts=?, "
                       "updated_ts=? WHERE work_id=?",
                       (json.dumps(result), rhash,
                        att.get("executed_config_hash"),
                        att.get("entry_state_hash"),
                        att.get("player_identity_hash"),
                        att.get("measurement_identity_hash"),
                        now(), now(), work_id))
            payload = {"attested": bool(att)}
            if att:
                payload["attestation"] = att
            if finding is not None:
                payload["finding"] = finding
            events.append(cx, r["world_id"], "WORK_COMPLETED", actor=worker_id,
                          refs={"work_id": work_id, "result_hash": rhash},
                          payload=payload)
            out = _work_dict(cx.execute("SELECT * FROM work_items WHERE "
                                        "work_id=?", (work_id,)).fetchone())
            if self.science_profile != "off":
                out["science"] = {"profile_findings":
                                  [] if finding is None else [finding]}
            return out

    def fail_work(self, work_id: str, worker_id: str, error: str, *,
                  retry: bool = True, claim_id: Optional[str] = None,
                  client_id: Optional[str] = None) -> dict:
        with self.store.write() as cx:
            r = self._owned_claim(cx, work_id, worker_id, {"CLAIMED", "RUNNING"},
                                  client_id=client_id, claim_id=claim_id)
            retryable = retry and r["attempts"] < r["max_attempts"]
            newst = "RETRYABLE" if retryable else "FAILED"
            cx.execute("UPDATE work_items SET status=?, claimed_by=NULL, "
                       "claim_id=NULL, lease_expires=NULL, error=?, "
                       "updated_ts=? WHERE work_id=?",
                       (newst, error, now(), work_id))
            events.append(cx, r["world_id"], "WORK_FAILED", actor=worker_id,
                          refs={"work_id": work_id},
                          payload={"error": error[:500], "next": newst})
            return _work_dict(cx.execute("SELECT * FROM work_items WHERE "
                                         "work_id=?", (work_id,)).fetchone())

    def get_work(self, work_id: str) -> dict:
        r = self.store.read().execute("SELECT * FROM work_items WHERE work_id=?",
                                      (work_id,)).fetchone()
        if r is None:
            raise NotFound("unknown work item", work_id=work_id)
        return _work_dict(r)

    # ================= budgets ==========================================
    def _init_budget(self, cx, world_id: str, budget: dict) -> None:
        limits = {}
        for res, spec in (budget or {}).items():
            if isinstance(spec, dict):
                limit, enf = spec.get("limit"), spec.get("enforcement",
                                                          "measured")
            else:
                limit, enf = spec, "measured"
            if enf not in ENFORCEMENT:
                raise ValidationError("bad enforcement class", resource=res,
                                      enforcement=enf, allowed=list(ENFORCEMENT))
            limits[res] = {"limit": limit, "enforcement": enf}
        cx.execute("INSERT INTO budgets(world_id,limits,consumed,updated_ts) "
                   "VALUES(?,?,?,?)",
                   (world_id, json.dumps(limits), json.dumps({}), now()))

    def _budget_rows(self, cx, world_row):
        """The budget rows governing `world_row`: its own LOCAL row and, for a
        fork child, the LINEAGE root's row -- the authoritative campaign budget
        that forking cannot multiply (H3). Pre-v2 worlds are their own root."""
        wid = world_row["world_id"]
        root = world_row["budget_root"] or wid
        out = []
        local = cx.execute("SELECT * FROM budgets WHERE world_id=?",
                           (wid,)).fetchone()
        if local is not None:
            out.append(("local", local))
        if root != wid:
            rb = cx.execute("SELECT * FROM budgets WHERE world_id=?",
                            (root,)).fetchone()
            if rb is not None:
                out.append(("lineage", rb))
        return root, out

    def _debit_budget(self, cx, world_row, resource: str, amount: float,
                      actor: str):
        """Debit `resource` on EVERY governing budget row (local safety cap AND
        lineage root) inside the caller's transaction. Returns (blocked, info).
        When any enforceable limit blocks: the exhaustion flag and (on the
        transition) a BUDGET_EXHAUSTED event are written durably, NOTHING is
        debited, and the caller must not proceed with the act this budget would
        have paid for (section 12: never fabricate enforcement)."""
        wid = world_row["world_id"]
        root, rows = self._budget_rows(cx, world_row)
        parsed, blocking = [], None
        for scope, b in rows:
            limits = json.loads(b["limits"])
            consumed = json.loads(b["consumed"])
            spec = limits.get(resource)
            prospective = consumed.get(resource, 0) + amount
            over = (spec and spec.get("limit") is not None
                    and spec["enforcement"] == "enforceable"
                    and prospective > spec["limit"])
            parsed.append((scope, b, consumed, spec, prospective))
            if over and blocking is None:
                blocking = (scope, b, spec, consumed.get(resource, 0))
        if blocking is not None:
            scope, b, spec, cur = blocking
            if not b["exhausted"]:
                cx.execute("UPDATE budgets SET exhausted=1, updated_ts=? "
                           "WHERE world_id=?", (now(), b["world_id"]))
                events.append(cx, wid, "BUDGET_EXHAUSTED", actor="foundry",
                              payload={"resource": resource,
                                       "limit": spec["limit"], "consumed": cur,
                                       "requested": amount, "scope": scope,
                                       "budget_root": root})
            return True, {"resource": resource, "limit": spec["limit"],
                          "consumed": cur, "scope": scope}
        total, lim = None, None
        for scope, b, consumed, spec, prospective in parsed:
            consumed[resource] = prospective
            cx.execute("UPDATE budgets SET consumed=?, updated_ts=? "
                       "WHERE world_id=?",
                       (json.dumps(consumed), now(), b["world_id"]))
            if scope == "local":
                total = prospective
                lim = spec.get("limit") if spec else None
        events.append(cx, wid, "BUDGET_CONSUMED", actor=actor,
                      payload={"resource": resource, "amount": amount,
                               "total": total, "budget_root": root})
        return False, {"resource": resource, "consumed": total, "limit": lim}

    def consume_budget(self, world_id: str, resource: str, amount: float, *,
                       client_id: Optional[str] = None) -> dict:
        """Account resource use and enforce limits at BOTH governing scopes:
        the world's local cap and its lineage root (H3). Exceeding an
        enforceable limit raises BudgetExhausted after durably recording the
        exhaustion (COMMIT-THEN-RAISE: raising inside the write() block would
        roll the transition back)."""
        with self.store.write() as cx:
            w = self._authorize_write(cx, world_id, client_id)
            blocked, info = self._debit_budget(cx, w, resource, amount,
                                               client_id or "foundry")
        if blocked:
            raise BudgetExhausted(
                "world resource budget exhausted", world_id=world_id, **info)
        return {**info, "exhausted": False}

    # ================= audit / third-party attestation ===================
    def engine_instance_id(self) -> str:
        """A stable id for THIS ENGINE INSTANCE, distinct from its build.

        R-SFE-2 (Mnemosyne, 2026-09-04). release.identity() returns
        engine_source_hash + source_commit, which identify the BUILD. Two
        engines running the same build are indistinguishable by it -- M1 and M2
        both reported engine_source_hash c358a53b for most of today, so a
        consumer holding an anchor could not tell WHICH engine minted it, and
        world ids are syntactically valid across both. This mints an instance
        id once, lazily, and stores it in the meta k/v table (no migration).
        It is minted ONCE and stored in the database, so it TRAVELS WITH THE
        SUBSTRATE rather than with the filesystem path: restoring this database
        elsewhere keeps the identity of the ledger it contains, which is the
        property an anchor consumer actually needs. It is deliberately NOT
        derived from the path -- a rollback that restores a backup to a
        different directory must not silently mint a new engine identity for
        the same events."""
        cx = self.store.read()
        row = cx.execute("SELECT value FROM meta WHERE key='engine_instance_id'"
                         ).fetchone()
        if row is not None:
            return row["value"]
        with self.store.write() as w:
            row = w.execute(               # re-read under the write lock
                "SELECT value FROM meta WHERE key='engine_instance_id'"
            ).fetchone()
            if row is not None:
                return row["value"]
            iid = "eng_" + secrets.token_hex(12)
            w.execute("INSERT OR IGNORE INTO meta(key,value) VALUES(?,?)",
                      ("engine_instance_id", iid))
            got = w.execute(
                "SELECT value FROM meta WHERE key='engine_instance_id'"
            ).fetchone()
            return got["value"]

    def engine_identity(self) -> dict:
        return {"engine_instance_id": self.engine_instance_id(),
                **release.identity()}

    def verify_anchor(self, world_id: str, event_id: str, entry_hash: str, *,
                      exp_id: Optional[str] = None,
                      obs_id: Optional[str] = None) -> dict:
        """Verify a causal anchor WITHOUT disclosing anything it protects.

        R-SFE-1 (Mnemosyne). PEW must be able to establish that an anchor on a
        fossil is genuine, and it does not hold the producing client's
        credential. This is deliberately NOT owner-scoped -- but it is also not
        a read: it returns booleans and the engine's identity, never payload,
        never refs, never content, and it cannot enumerate. To ask a question
        at all you must already possess the 256-bit entry_hash, which is only
        obtainable from the producer or from the fossil the producer published.

        CRITICALLY, this enforces BINDING, not merely existence. Harmonia's D1
        showed that checking a (event_id, entry_hash) pair EXISTS lets a
        wrong-but-real event pass every downstream check -- anchoring on
        WORLD_CREATED would satisfy a pure existence test. So when the caller
        names the exp_id or obs_id the anchor is CLAIMED to belong to, this
        checks the event actually references it. That is what makes
        'wrong real event -> rejected' enforceable in PEW."""
        cx = self.store.read()
        r = cx.execute(
            "SELECT event_id, world_id, event_type, entry_hash, refs, "
            "event_seq, world_index FROM events WHERE event_id=? AND world_id=?",
            (event_id, world_id)).fetchone()
        checks = {"event_exists": r is not None, "entry_hash_matches": False,
                  "binds_exp_id": None, "binds_obs_id": None}
        out = {"valid": False, "checks": checks,
               "engine": self.engine_identity()}
        if r is None:
            return out                      # uniform answer; discloses nothing
        # constant-shape comparison: a mismatched hash is indistinguishable
        # from a missing event in everything but the checks block
        checks["entry_hash_matches"] = (r["entry_hash"] == entry_hash)
        if not checks["entry_hash_matches"]:
            return out
        refs = json.loads(r["refs"] or "{}")
        if exp_id is not None:
            checks["binds_exp_id"] = (refs.get("exp_id") == exp_id)
        if obs_id is not None:
            checks["binds_obs_id"] = (refs.get("obs_id") == obs_id)
        out["event_type"] = r["event_type"]
        out["event_seq"] = r["event_seq"]
        out["world_index"] = r["world_index"]
        out["valid"] = (checks["entry_hash_matches"]
                        and checks["binds_exp_id"] is not False
                        and checks["binds_obs_id"] is not False)
        return out

    def audit_envelope(self, world_id: str, exp_id: str, *,
                       client_id: Optional[str] = None) -> dict:
        """The complete immutable material for ONE experiment, sealed.

        R2-1 (Harmonia). The sealed record exists in SFE but its read routes
        are client-scoped, so a third-party investigator holding a PEW fossil
        gets 403 and cannot reconstruct what ran. The fix is NOT to let an
        arbitrary investigator bypass SFE authorization. It is for the PRODUCER
        -- who legitimately holds the credential -- to export a self-contained,
        hash-sealed envelope that PEW stores immutably and serves to anyone.

            producer -> SFE sealed record -> PEW immutable audit envelope

        So this call is OWNER-SCOPED exactly like every other read: ordinary
        client isolation is untouched. What changes is that the material can
        now LEAVE the engine as one verifiable object instead of five
        credentialed reads.

        envelope_hash seals the whole document, and every identity inside it is
        independently checkable: spec against the sealed spec_hash in the
        ledger, and the anchors against verify_anchor(), which needs no
        credential."""
        cx = self.store.read()
        w = self._authorize(cx, world_id, client_id)      # isolation preserved
        ex = cx.execute("SELECT * FROM experiments WHERE exp_id=? AND "
                        "world_id=?", (exp_id, world_id)).fetchone()
        if ex is None:
            raise NotFound("experiment not in this world", exp_id=exp_id)

        obs = [_observation_dict(o) for o in cx.execute(
            "SELECT * FROM observations WHERE world_id=? AND exp_id=? "
            "ORDER BY created_seq", (world_id, exp_id)).fetchall()]

        # the ledger events that BIND this experiment: its commit (which seals
        # spec_hash + engine build) and each observation's causal anchor
        anchors = []
        for e in cx.execute(
                "SELECT event_id, event_type, entry_hash, event_seq, "
                "world_index, refs, ts FROM events WHERE world_id=? "
                "ORDER BY world_index", (world_id,)).fetchall():
            refs = json.loads(e["refs"] or "{}")
            if refs.get("exp_id") != exp_id:
                continue
            anchors.append({"event_id": e["event_id"],
                            "event_type": e["event_type"],
                            "entry_hash": e["entry_hash"],
                            "event_seq": e["event_seq"],
                            "world_index": e["world_index"], "ts": e["ts"],
                            "refs": refs})

        committed = next((a for a in anchors
                          if a["event_type"] == "EXPERIMENT_COMMITTED"), None)
        sealed_spec_hash = None
        if committed is not None:
            ev = cx.execute("SELECT payload FROM events WHERE event_id=?",
                            (committed["event_id"],)).fetchone()
            sealed_spec_hash = json.loads(ev["payload"]).get("spec_hash")

        work = None
        if ex["work_id"]:
            wr = cx.execute("SELECT work_id, status, result_hash, dedup_key "
                            "FROM work_items WHERE work_id=?",
                            (ex["work_id"],)).fetchone()
            if wr is not None:
                work = {"work_id": wr["work_id"], "status": wr["status"],
                        "result_hash": wr["result_hash"]}

        body = {
            "envelope_version": "sfe.audit_envelope.v1",
            "engine": self.engine_identity(),
            "api_version": "v2",
            "schema_version": SCHEMA_VERSION,
            "world": {**_world_dict(w),
                      "budget": self._budget_config(cx, world_id)},
            "experiment": _experiment_dict(ex),
            "sealed_spec_hash_in_ledger": sealed_spec_hash,
            "spec_hash_recomputed": content_hash(json.loads(ex["spec"])),
            "observations": obs,
            "work": work,
            "anchors": anchors,
            "ledger_head_hash": w["head_hash"],
            # v7: FAMILY AND ARM SURVIVE FOSSILIZATION.
            #
            # families/family_members is the engine's only cross-world
            # container, and the envelope is the only thing that LEAVES the
            # engine as one verifiable object. Before this, an exported fossil
            # could not say that its experiment was arm B of a twelve-member
            # campaign -- the membership stayed behind in a table the fossil's
            # reader has no credential for, so best-of-N was invisible again at
            # exactly the moment the record left the building.
            #
            # Included by VALUE, not by reference, for the same reason the
            # envelope exists at all: a third party holding the fossil has no
            # SFE credential and cannot resolve a family_id. envelope_hash
            # seals this with everything else.
            "families": self._envelope_families(cx, world_id, exp_id),
        }
        body["envelope_hash"] = content_hash(body)
        return body

    def _envelope_families(self, cx, world_id: str, exp_id: str) -> list:
        """Every family this experiment or its world belongs to, with the
        member's role and the family's sealed manifest hash."""
        out = []
        rows = cx.execute(
            "SELECT fm.family_id, fm.member_kind, fm.member_id, fm.role, "
            "fm.arm AS arm, "
            "f.kind AS family_kind, f.manifest AS manifest, "
            "f.manifest_hash AS manifest_hash, f.state AS state "
            "FROM family_members fm JOIN families f "
            "ON f.family_id = fm.family_id "
            "WHERE (fm.member_kind IN ('experiment','analysis') "
            "       AND fm.member_id = ?) "
            "   OR (fm.member_kind = 'world' AND fm.member_id = ?) "
            "ORDER BY fm.family_id", (exp_id, world_id)).fetchall()
        for r in rows:
            try:
                manifest = json.loads(r["manifest"])
            except (TypeError, ValueError):
                manifest = {}
            # ARM RULING: from the sealed DESIGN (the append-only member
            # record), never from the execution spec -- so two arms may carry
            # an identical execution hash.
            arm = r["arm"]
            declared_arms = manifest.get("arms")
            census = cx.execute(
                "SELECT COUNT(*) n, SUM(role='selected') sel, "
                "SUM(role='alternative') alt FROM family_members "
                "WHERE family_id=?", (r["family_id"],)).fetchone()
            out.append({
                "family_id": r["family_id"], "family_kind": r["family_kind"],
                "state": r["state"], "manifest_hash": r["manifest_hash"],
                "member_kind": r["member_kind"], "member_id": r["member_id"],
                "role": r["role"],
                "arm": arm,
                "declared_arms": declared_arms,
                "family_member_count": census["n"],
                "selected": census["sel"] or 0,
                "alternatives": census["alt"] or 0,
                # the property that makes best-of-N legible, carried OUT with
                # the fossil rather than left behind in the engine
                "selection_visible": bool((census["sel"] or 0) >= 1
                                          and (census["alt"] or 0) >= 1)})
        return out

    def get_experiment(self, world_id: str, exp_id: str, *,
                       client_id: Optional[str] = None) -> dict:
        """The frozen experiment specification -- the EXACT ACTION of a run.

        D-REPLAY-1 (2026-09-04). The engine has always SEALED the action's
        identity: EXPERIMENT_COMMITTED carries spec_hash and engine_source_hash
        in the tamper-evident chain. But the spec PREIMAGE had no read path, so
        a consumer could VERIFY a spec it already held and could never RECOVER
        one it did not. That is the precise mechanism behind Harmonia's "replay
        is not self-contained": the action was not missing from the engine, it
        was unreachable from outside it, and so lived only in whatever repo
        checkout happened to produce the run.

        Returning spec WITH spec_hash lets any consumer re-derive the hash and
        check it against the sealed ledger payload -- recovery and verification
        in one call."""
        cx = self.store.read()
        self._authorize(cx, world_id, client_id)
        r = cx.execute("SELECT * FROM experiments WHERE exp_id=? AND world_id=?",
                       (exp_id, world_id)).fetchone()
        if r is None:
            raise NotFound("experiment not in this world", exp_id=exp_id)
        return _experiment_dict(r)

    def list_experiments(self, world_id: str, *,
                         client_id: Optional[str] = None,
                         state: Optional[str] = None) -> list:
        cx = self.store.read()
        self._authorize(cx, world_id, client_id)
        q, a = "SELECT * FROM experiments WHERE world_id=?", [world_id]
        if state:
            q += " AND state=?"; a.append(state)
        q += " ORDER BY created_seq"
        return [_experiment_dict(r) for r in cx.execute(q, tuple(a)).fetchall()]

    def list_observations(self, world_id: str, *,
                          client_id: Optional[str] = None,
                          exp_id: Optional[str] = None) -> list:
        """The recorded outcomes, with their evidence class and role. Needed to
        COMPARE a replay against the run it replays."""
        cx = self.store.read()
        self._authorize(cx, world_id, client_id)
        q, a = "SELECT * FROM observations WHERE world_id=?", [world_id]
        if exp_id:
            q += " AND exp_id=?"; a.append(exp_id)
        q += " ORDER BY created_seq"
        return [_observation_dict(r) for r in cx.execute(q, tuple(a)).fetchall()]

    def _budget_config(self, cx, world_id: str) -> dict:
        """The world's budget LIMITS as configured -- the part of the world's
        identity a replay must reproduce. Live consumption is deliberately NOT
        here: it is state, not configuration, and belongs to /resources."""
        b = cx.execute("SELECT limits FROM budgets WHERE world_id=?",
                       (world_id,)).fetchone()
        return json.loads(b["limits"]) if b is not None else {}

    def budget_status(self, world_id: str) -> dict:
        cx = self.store.read()
        w = cx.execute("SELECT world_id, budget_root FROM worlds WHERE "
                       "world_id=?", (world_id,)).fetchone()
        if w is None:
            raise NotFound("unknown world", world_id=world_id)
        b = cx.execute("SELECT * FROM budgets WHERE world_id=?",
                       (world_id,)).fetchone()
        if b is None:
            raise NotFound("world has no budget row", world_id=world_id)
        root = w["budget_root"] or world_id
        out = {"limits": json.loads(b["limits"]),
               "consumed": json.loads(b["consumed"]),
               "exhausted": bool(b["exhausted"]),
               "budget_root": root,
               "scope": "LINEAGE_ROOT" if root == world_id else "FORK_LOCAL"}
        if root != world_id:
            rb = cx.execute("SELECT * FROM budgets WHERE world_id=?",
                            (root,)).fetchone()
            if rb is not None:
                out["lineage"] = {"limits": json.loads(rb["limits"]),
                                  "consumed": json.loads(rb["consumed"]),
                                  "exhausted": bool(rb["exhausted"])}
        return out

    # ================= research objects ==================================
    def propose_hypothesis(self, world_id: str, statement: str, *,
                           client_id: Optional[str] = None,
                           parents: Optional[list] = None,
                           idem_key: Optional[str] = None,
                           request_hash: Optional[str] = None) -> str:
        hid = new_id("hypothesis")
        with self.store.write() as cx:
            r = self._authorize_write(cx, world_id, client_id)
            replay = self._idem_check(cx, r["client_id"], idem_key, request_hash)
            if replay is not None:
                return replay
            ev = events.append(cx, world_id, "HYPOTHESIS_PROPOSED",
                               actor=r["client_id"], refs={"hyp_id": hid},
                               payload={"statement": statement})
            cx.execute("INSERT INTO hypotheses(hyp_id,world_id,statement,"
                       "content_hash,created_ts,created_seq) VALUES(?,?,?,?,?,?)",
                       (hid, world_id, statement, content_hash(statement),
                        now(), ev["event_seq"]))
            for p in (parents or []):
                self._edge(cx, world_id, r["client_id"], p["kind"], p["id"],
                           "hypothesis", hid, "DERIVES_FROM")
            self._idem_record(cx, r["client_id"], idem_key, world_id,
                              "hypotheses", request_hash, hid)
        return hid

    def register_prediction(self, world_id: str, hyp_id: str, content: dict, *,
                            client_id: Optional[str] = None,
                            idem_key: Optional[str] = None,
                            request_hash: Optional[str] = None) -> str:
        """Register a SEALED prediction. Its content hash and its event_seq are
        frozen now, so a prediction cannot be edited post-hoc and its temporal
        position is authoritative (I6)."""
        pid = new_id("prediction")
        with self.store.write() as cx:
            r = self._authorize_write(cx, world_id, client_id)
            replay = self._idem_check(cx, r["client_id"], idem_key, request_hash)
            if replay is not None:
                return replay
            if cx.execute("SELECT 1 FROM hypotheses WHERE hyp_id=? AND "
                          "world_id=?", (hyp_id, world_id)).fetchone() is None:
                raise NotFound("hypothesis not in this world", hyp_id=hyp_id)
            ph = content_hash(content)
            ev = events.append(cx, world_id, "PREDICTION_REGISTERED",
                               actor=r["client_id"],
                               refs={"pred_id": pid, "hyp_id": hyp_id},
                               payload={"content_hash": ph})
            cx.execute("INSERT INTO predictions(pred_id,world_id,hyp_id,content,"
                       "content_hash,created_ts,created_seq) "
                       "VALUES(?,?,?,?,?,?,?)",
                       (pid, world_id, hyp_id, json.dumps(content), ph, now(),
                        ev["event_seq"]))
            cx.execute("UPDATE hypotheses SET state='PREDICTED' WHERE hyp_id=? "
                       "AND state='PROPOSED'", (hyp_id,))
            self._idem_record(cx, r["client_id"], idem_key, world_id,
                              "predictions", request_hash, pid)
        return pid

    def create_experiment(self, world_id: str, spec: dict, *,
                          client_id: Optional[str] = None,
                          hyp_id: Optional[str] = None,
                          pred_id: Optional[str] = None,
                          commit: bool = True,
                          enqueue: bool = False, kind: str = "experiment",
                          priority: int = 100,
                          unit_of_analysis: Optional[str] = None,
                          declared_n: Optional[int] = None,
                          source_set: Optional[list] = None,
                          idem_key: Optional[str] = None,
                          request_hash: Optional[str] = None) -> dict:
        """REGISTER an experiment and (by default) COMMIT it atomically in the
        same transaction. Registration alone (commit=False) is PLANNING: the
        experiment exists but is non-executable, consumes no budget, and its
        prospective-prediction window is still open. `enqueue` requires commit
        -- nothing is ever released for execution without crossing the commit
        boundary (see commit_experiment for the governing rule).

        F5: an idem_key makes a SUCCESSFUL create+commit retry-safe (no
        duplicate experiment, no second budget debit). A budget-BLOCKED create
        is not cached (a retry re-registers), which is harmless -- both are
        blocked and neither debits."""
        if enqueue and not commit:
            raise ValidationError(
                "enqueue requires commit: an experiment cannot be released for "
                "execution without crossing the commit boundary")
        # v6: an ANALYSIS is an experiment that declares a SOURCE SET. It is
        # deliberately not a parallel object stack -- an analysis has a
        # specification, is sealed by spec_hash, crosses the same irreversible
        # commit boundary, and must not be edited after its result is known.
        # Those are the properties the experiment lifecycle already provides,
        # and a second stack would have had to reimplement every one of them.
        # The DURABLE marker is source_set_hash, not the work item's kind: kind
        # only exists once an experiment is committed with enqueue, so a
        # registered-but-uncommitted analysis would otherwise have no identity.
        if source_set is not None:
            if not isinstance(source_set, list):
                raise ValidationError("source_set must be a list of ids")
            if unit_of_analysis is None:
                raise ValidationError(
                    "an analysis with a source_set must declare a "
                    "unit_of_analysis",
                    allowed=sorted(UNITS_OF_ANALYSIS))
        if (unit_of_analysis is not None or declared_n is not None) \
                and source_set is None:
            raise ValidationError(
                "unit_of_analysis/declared_n describe a source_set; supply one")
        source_set_hash = None
        if source_set is not None:
            # ORDER-INDEPENDENT and WORLD-INDEPENDENT: the same evidentiary base
            # hashes identically no matter who assembled it or in what order,
            # which is what makes "these two analyses used the same sources" a
            # comparison rather than a claim.
            source_set_hash = content_hash(sorted(
                x if isinstance(x, str) else json.dumps(x, sort_keys=True)
                for x in source_set))
        eid = new_id("experiment")
        out = {"exp_id": eid, "work_id": None, "committed_seq": None}
        blocked_info = None
        with self.store.write() as cx:
            r = self._authorize_write(cx, world_id, client_id)
            replay = self._idem_check(cx, r["client_id"], idem_key, request_hash)
            if replay is not None:
                return replay
            if pred_id is not None and cx.execute(
                    "SELECT 1 FROM predictions WHERE pred_id=? AND world_id=?",
                    (pred_id, world_id)).fetchone() is None:
                raise NotFound("prediction not in this world", pred_id=pred_id)
            ev = events.append(cx, world_id, "EXPERIMENT_CREATED",
                               actor=r["client_id"],
                               refs={"exp_id": eid, "hyp_id": hyp_id,
                                     "pred_id": pred_id})
            cx.execute("INSERT INTO experiments(exp_id,world_id,hyp_id,pred_id,"
                       "spec,spec_hash,unit_of_analysis,declared_n,"
                       "source_set_hash,created_ts,created_seq) "
                       "VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                       (eid, world_id, hyp_id, pred_id, json.dumps(spec),
                        content_hash(spec), unit_of_analysis, declared_n,
                        source_set_hash, now(), ev["event_seq"]))
            if source_set_hash is not None:
                ver = {"unit_of_analysis": unit_of_analysis,
                       "declared_n": declared_n,
                       "source_set_hash": source_set_hash,
                       "profile": self.science_profile}
                if self.science_profile != "off":
                    ver.update(self._verify_units(
                        cx, r["client_id"], unit_of_analysis, source_set))
                    ver["unit_mismatch"] = (
                        declared_n is not None
                        and declared_n != ver["verified_n"])
                    if self.science_profile == "strict" and ver["unit_mismatch"]:
                        raise ValidationError(
                            "science-profile=strict: declared_n does not match "
                            "the number of distinct units the engine counted "
                            "in the source set",
                            unit_of_analysis=unit_of_analysis,
                            declared_n=declared_n,
                            verified_n=ver["verified_n"],
                            sources_unresolved=ver["sources_unresolved"])
                events.append(cx, world_id, "ANALYSIS_REGISTERED",
                              actor=r["client_id"], refs={"exp_id": eid},
                              payload=ver)
                out["analysis"] = ver
            if hyp_id:
                self._edge(cx, world_id, r["client_id"], "hypothesis", hyp_id,
                           "experiment", eid, "TESTS")
            if commit:
                blocked_info, commit_out = self._commit_core(
                    cx, r, eid, enqueue=enqueue, kind=kind, priority=priority)
                if blocked_info is None:
                    out.update(commit_out)
            if blocked_info is None:      # record for retry-safety on success
                self._idem_record(cx, r["client_id"], idem_key, world_id,
                                  "experiments", request_hash, out)
        if blocked_info is not None:
            # COMMIT-THEN-RAISE: the registration and the durable exhaustion
            # record persist; the experiment remains REGISTERED, non-executable.
            raise BudgetExhausted(
                "experiment registered but NOT committed: budget exhausted",
                world_id=world_id, exp_id=eid, **blocked_info)
        return out

    def _commit_core(self, cx, world_row, exp_id: str, *, enqueue: bool,
                     kind: str, priority: int):
        """The REGISTERED -> COMMITTED transition, inside the caller's open
        transaction. Returns (blocked_info, out): blocked_info is not None when
        the budget blocked the commit (exhaustion markers written durably;
        nothing else changed); otherwise out carries committed_seq / work_id.
        Idempotent: an already-committed experiment returns its recorded
        boundary with NO second debit (D2-03)."""
        wid = world_row["world_id"]
        ex = cx.execute("SELECT * FROM experiments WHERE exp_id=? AND "
                        "world_id=?", (exp_id, wid)).fetchone()
        if ex is None:
            raise NotFound("experiment not in this world", exp_id=exp_id)
        if ex["committed_seq"] is not None:
            return None, {"committed_seq": ex["committed_seq"],
                          "work_id": ex["work_id"], "already_committed": True}
        if world_row["state"] != "RUNNING":
            raise InvalidTransition(
                "world must be RUNNING to commit an experiment",
                world_id=wid, state=world_row["state"])
        blocked, info = self._debit_budget(cx, world_row, "experiments", 1,
                                           world_row["client_id"])
        if blocked:
            return info, None
        ev = events.append(
            cx, wid, "EXPERIMENT_COMMITTED", actor=world_row["client_id"],
            refs={"exp_id": exp_id, "hyp_id": ex["hyp_id"],
                  "pred_id": ex["pred_id"]},
            payload={"spec_hash": ex["spec_hash"],
                     "engine_source_hash": release.ENGINE_SOURCE_HASH,
                     "budget_resource": "experiments",
                     "prospective_rule":
                         "predictions with created_seq < committed_seq"})
        cx.execute("UPDATE experiments SET committed_seq=?, committed_ts=? "
                   "WHERE exp_id=?", (ev["event_seq"], now(), exp_id))
        wk = None
        if enqueue:
            wk = new_id("work")
            cx.execute(
                "INSERT INTO work_items(work_id,world_id,kind,payload,"
                "priority,created_ts,updated_ts) VALUES(?,?,?,?,?,?,?)",
                (wk, wid, kind,
                 json.dumps({"exp_id": exp_id, **json.loads(ex["spec"])}),
                 priority, now(), now()))
            cx.execute("UPDATE experiments SET work_id=? WHERE exp_id=?",
                       (wk, exp_id))
            events.append(cx, wid, "WORK_ENQUEUED",
                          actor=world_row["client_id"],
                          refs={"work_id": wk, "exp_id": exp_id})
        return None, {"committed_seq": ev["event_seq"], "work_id": wk}

    def commit_experiment(self, world_id: str, exp_id: str, *,
                          client_id: Optional[str] = None,
                          enqueue: bool = False, kind: str = "experiment",
                          priority: int = 100) -> dict:
        """The IRREVERSIBLE scientific boundary (the governing GEN-2 lifecycle
        invariant). In ONE atomic transaction this: freezes the experiment's
        specification (spec_hash sealed in the event), CLOSES the prospective-
        prediction window -- only predictions with created_seq < committed_seq
        can EVER be prospective for this experiment -- debits the authoritative
        experiment budget at both governing scopes (local + lineage root),
        records EXPERIMENT_COMMITTED stamped with the exact running engine
        source hash, and optionally releases the experiment for execution by
        enqueuing work. After this transaction commits, hindsight cannot
        acquire prospective status: a worker may learn the outcome, but the
        window closed BEFORE execution became possible.

        Idempotent (no second debit). A budget block leaves the experiment
        REGISTERED and non-executable, with the exhaustion durably recorded
        (COMMIT-THEN-RAISE)."""
        with self.store.write() as cx:
            r = self._authorize_write(cx, world_id, client_id)
            blocked_info, out = self._commit_core(
                cx, r, exp_id, enqueue=enqueue, kind=kind, priority=priority)
        if blocked_info is not None:
            raise BudgetExhausted(
                "experiment NOT committed: budget exhausted",
                world_id=world_id, exp_id=exp_id, **blocked_info)
        return {"exp_id": exp_id, **out}

    def record_observation(self, world_id: str, exp_id: str, content: dict,
                           outcome: str, *, client_id: Optional[str] = None,
                           pred_id: Optional[str] = None,
                           work_id: Optional[str] = None,
                           retrospective: bool = False,
                           replication: bool = False,
                           idem_key: Optional[str] = None,
                           request_hash: Optional[str] = None) -> str:
        """Record an observation on a COMMITTED experiment.

        DUPLICATE BINDING (F3): the FIRST observation bound to a prediction is
        the ORIGINAL adjudication relation and fixes the prediction's epistemic
        status. A later observation bound to the SAME prediction is rejected
        unless it is an EXPLICIT replication=True, in which case it is recorded
        as evidence_role=REPLICATION and can NEVER improve (re-adjudicate) the
        original -- a replication is a retest, not a rewrite. Replication is
        typed, never inferred from a duplicate.

        PROSPECTIVE RULE (DFX-1): a bound prediction is prospective iff it was
        registered BEFORE the experiment's commit (pred.created_seq <
        exp.committed_seq). The commit closed the window BEFORE execution
        became possible, so neither a prior observation nor a worker's local
        knowledge of the outcome can be laundered into foresight. A post-commit
        prediction may be recorded only when the caller EXPLICITLY marks it
        retrospective=True -- it is preserved, but excluded from prospective
        status forever (D1-03/D1-08). No later observation reopens the window.

        EVIDENCE AUTHORITY (H4): pass work_id to bind this observation to the
        authoritative completed work result (verified: same world, COMPLETED,
        enqueued for THIS experiment) -> evidence_class ENGINE_WORK_RESULT.
        Otherwise the class is CLIENT_ASSERTED, and that class is recorded on
        the observation, the event, and any CLAIM_* adjudication -- a client
        assertion can never masquerade as an engine-attested result."""
        if outcome not in ("FALSIFIED", "SURVIVED", "INCONCLUSIVE"):
            raise ValidationError("bad outcome", outcome=outcome)
        oid = new_id("observation")
        with self.store.write() as cx:
            r = self._authorize_write(cx, world_id, client_id)
            replay = self._idem_check(cx, r["client_id"], idem_key, request_hash)
            if replay is not None:
                return replay
            ex = cx.execute("SELECT * FROM experiments WHERE exp_id=? AND "
                            "world_id=?", (exp_id, world_id)).fetchone()
            if ex is None:
                raise NotFound("experiment not in this world", exp_id=exp_id)
            if ex["committed_seq"] is None:
                raise InvalidTransition(
                    "experiment is not committed; the commit boundary must "
                    "close the prospective window before any outcome can be "
                    "recorded", exp_id=exp_id)
            evidence_class, ev_work_refs = "CLIENT_ASSERTED", {}
            # D-ATTEST-1 (2026-09-04): a world may be created with
            # require_attestation=true, which makes the DEGRADED evidence class
            # unreachable in that world instead of merely visible after the
            # fact. Harmonia's C3 showed the engine types the class honestly but
            # nothing FORCES it -- an orchestrator that omits one identifier
            # silently produces CLIENT_ASSERTED "evidence", and only a separate
            # status read reveals which class it got. Fail closed, at the write.
            if r["require_attestation"] and work_id is None:
                raise ValidationError(
                    "this world requires engine-attested evidence: pass the "
                    "work_id of the COMPLETED work item that produced this "
                    "observation. The world was created with "
                    "require_attestation=true, so CLIENT_ASSERTED observations "
                    "are refused here rather than silently recorded as a weaker "
                    "evidence class.",
                    world_id=world_id, exp_id=exp_id,
                    required_evidence_class="ENGINE_WORK_RESULT")
            if work_id is not None:
                wrow = cx.execute("SELECT * FROM work_items WHERE work_id=?",
                                  (work_id,)).fetchone()
                if (wrow is None or wrow["world_id"] != world_id
                        or wrow["status"] != "COMPLETED"):
                    raise ValidationError(
                        "work_id does not name a COMPLETED work item of this "
                        "world; refusing ENGINE_WORK_RESULT evidence class",
                        work_id=work_id)
                wpayload = json.loads(wrow["payload"])
                if wpayload.get("exp_id") != exp_id and ex["work_id"] != work_id:
                    raise ValidationError(
                        "work item was not enqueued for this experiment; "
                        "refusing ENGINE_WORK_RESULT evidence class",
                        work_id=work_id, exp_id=exp_id)
                evidence_class = "ENGINE_WORK_RESULT"
                ev_work_refs = {"work_id": work_id,
                                "result_hash": wrow["result_hash"]}
            prospective = None
            if pred_id is not None:
                p = cx.execute("SELECT created_seq FROM predictions WHERE "
                               "pred_id=? AND world_id=?",
                               (pred_id, world_id)).fetchone()
                if p is None:
                    raise NotFound("prediction not in this world",
                                   pred_id=pred_id)
                prospective = (1 if p["created_seq"] < ex["committed_seq"]
                               else 0)
                if not prospective and not retrospective:
                    raise PredictionOrderingError(
                        "prediction was registered AFTER the experiment's "
                        "commit closed the prospective window; it can only be "
                        "recorded with retrospective=true and is never "
                        "prospective", pred_id=pred_id,
                        prediction_seq=p["created_seq"],
                        committed_seq=ex["committed_seq"])
            # F3: the FIRST outcome-bearing observation of an experiment is its
            # ORIGINAL result; likewise the first binding of a prediction. A
            # REPEAT -- another observation of the SAME experiment (with OR
            # without a prediction), or another binding of the SAME prediction --
            # must be an explicit replication (typed, never inferred) and NEVER
            # re-adjudicates. Keying on the experiment (not only the prediction)
            # closes the pred_id=None and cross-prediction re-adjudication paths.
            prior_exp = cx.execute(
                "SELECT COUNT(*) n FROM observations WHERE world_id=? AND "
                "exp_id=?", (world_id, exp_id)).fetchone()["n"]
            prior_pred = 0 if pred_id is None else cx.execute(
                "SELECT COUNT(*) n FROM observations WHERE world_id=? AND "
                "pred_id=?", (world_id, pred_id)).fetchone()["n"]
            is_repeat = prior_exp > 0 or prior_pred > 0
            if is_repeat and not replication:
                raise ConflictError(
                    "this experiment (or prediction) already has an ORIGINAL "
                    "observation; a later observation must set replication=true "
                    "and is a retest that can never re-adjudicate the original",
                    exp_id=exp_id, pred_id=pred_id)
            evidence_role = "REPLICATION" if is_repeat else "ORIGINAL"
            if pred_id is not None:
                cx.execute("UPDATE predictions SET state='OBSERVED' WHERE "
                           "pred_id=?", (pred_id,))
            ev = events.append(cx, world_id, "OBSERVATION_RECORDED",
                               actor=r["client_id"],
                               refs={"obs_id": oid, "exp_id": exp_id,
                                     "pred_id": pred_id, **ev_work_refs},
                               payload={"outcome": outcome,
                                        "prospective": prospective,
                                        "evidence_class": evidence_class,
                                        "evidence_role": evidence_role})
            cx.execute("INSERT INTO observations(obs_id,world_id,exp_id,pred_id,"
                       "content,outcome,pred_prospective,evidence_class,"
                       "evidence_role,work_id,created_ts,created_seq) "
                       "VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                       (oid, world_id, exp_id, pred_id, json.dumps(content),
                        outcome, prospective, evidence_class, evidence_role,
                        work_id, now(), ev["event_seq"]))
            cx.execute("UPDATE experiments SET state='OBSERVED' WHERE exp_id=?",
                       (exp_id,))
            # ADJUDICATION happens only on the ORIGINAL observation, and
            # FALSIFICATION IS MONOTONIC: a SURVIVED observation can NEVER
            # un-falsify a hypothesis, and CLAIM_* is emitted ONLY on a real
            # state transition (no superseding / duplicate claims). This makes
            # adjudication once-and-fixed against laundering, while still letting
            # a later independent experiment legitimately FALSIFY a hypothesis
            # that earlier survived (survived -> falsified, never the reverse).
            if ex["hyp_id"] and evidence_role == "ORIGINAL":
                cur = cx.execute("SELECT state FROM hypotheses WHERE hyp_id=?",
                                 (ex["hyp_id"],)).fetchone()["state"]
                new = None
                if outcome == "FALSIFIED" and cur != "FALSIFIED":
                    new = "FALSIFIED"
                elif outcome == "SURVIVED" and cur not in ("SURVIVED",
                                                           "FALSIFIED"):
                    new = "SURVIVED"
                if new is not None:
                    cx.execute("UPDATE hypotheses SET state=? WHERE hyp_id=?",
                               (new, ex["hyp_id"]))
                    # provenance SURVIVES adjudication (H4): the claim event
                    # carries the evidence class and prospective status.
                    events.append(cx, world_id,
                                  "CLAIM_FALSIFIED" if new == "FALSIFIED"
                                  else "CLAIM_SURVIVED", actor=r["client_id"],
                                  refs={"hyp_id": ex["hyp_id"], "obs_id": oid},
                                  payload={"prospective": prospective,
                                           "evidence_class": evidence_class})
            # D-ANCHOR-1 (2026-09-04): return the EXACT causal identifiers of
            # the event this call just appended. Harmonia's D1 showed a
            # downstream consumer (PEW) can only check that an (event_id,
            # entry_hash) pair EXISTS -- not that it is THIS run's observation
            # -- so an agent that searched the ledger could anchor a fossil to
            # WORLD_CREATED and pass every shape check. Returning the anchor
            # from the write removes the search, and with it the class of
            # wrong-but-real anchors: the caller never has to guess which event
            # was its own.
            out = {"obs_id": oid, "event_id": ev["event_id"],
                   "entry_hash": ev["entry_hash"],
                   "event_seq": ev["event_seq"],
                   "world_index": ev["world_index"],
                   "evidence_class": evidence_class,
                   "evidence_role": evidence_role}
            self._idem_record(cx, r["client_id"], idem_key, world_id,
                              "observations", request_hash, out)
        return out

    def record_failure(self, world_id: str, *, failure_type: str,
                       falsifier: str, violated: str,
                       client_id: Optional[str] = None,
                       experiment_id: Optional[str] = None,
                       hypothesis_id: Optional[str] = None,
                       prediction_id: Optional[str] = None,
                       reference: Any = None, expected: Any = None,
                       observed: Any = None, measurement_id: Optional[str] = None,
                       artifact_refs: Optional[list] = None,
                       reproducibility: str = "UNKNOWN",
                       extensions: Optional[dict] = None,
                       idem_key: Optional[str] = None,
                       request_hash: Optional[str] = None) -> str:
        fid = new_id("failure")
        with self.store.write() as cx:
            r = self._authorize_write(cx, world_id, client_id)
            replay = self._idem_check(cx, r["client_id"], idem_key, request_hash)
            if replay is not None:
                return replay
            ev = events.append(cx, world_id, "FAILURE_RECORDED",
                               actor=r["client_id"], refs={"failure_id": fid,
                               "experiment_id": experiment_id},
                               payload={"failure_type": failure_type})
            cx.execute(
                "INSERT INTO failures(failure_id,world_id,experiment_id,"
                "hypothesis_id,prediction_id,failure_type,reference,expected,"
                "observed,falsifier,violated,measurement_id,artifact_refs,"
                "reproducibility,extensions,created_ts,created_seq) "
                "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (fid, world_id, experiment_id, hypothesis_id, prediction_id,
                 failure_type, json.dumps(reference), json.dumps(expected),
                 json.dumps(observed), falsifier, violated, measurement_id,
                 json.dumps(artifact_refs or []), reproducibility,
                 json.dumps(extensions or {}), now(), ev["event_seq"]))
            self._idem_record(cx, r["client_id"], idem_key, world_id,
                              "failures", request_hash, fid)
        return fid

    def consume_failure(self, world_id: str, failure_id: str, dst_kind: str,
                        dst_id: str, *, client_id: Optional[str] = None) -> str:
        """Record an agent's CLAIM that a failure was used to produce a
        downstream object. This is a CLAIMED reference only -- whether it was
        causally or empirically useful is a separate, measurable question
        (section 8)."""
        with self.store.write() as cx:
            r = self._authorize_write(cx, world_id, client_id)
            if cx.execute("SELECT 1 FROM failures WHERE failure_id=? AND "
                          "world_id=?", (failure_id, world_id)).fetchone() is None:
                raise NotFound("failure not in this world", failure_id=failure_id)
            eid = self._edge(cx, world_id, r["client_id"], "failure",
                             failure_id, dst_kind, dst_id, "CONSUMED_BY")
            events.append(cx, world_id, "FAILURE_CONSUMED", actor=r["client_id"],
                          refs={"failure_id": failure_id, "dst_id": dst_id,
                                "dst_kind": dst_kind})
        return eid

    def _edge(self, cx, world_id, actor, src_kind, src_id, dst_kind, dst_id,
              relation, claimed=1) -> str:
        eid = new_id("edge")
        ev = events.append(cx, world_id, "LINEAGE_EDGE_ADDED", actor=actor,
                           refs={"src": src_id, "dst": dst_id,
                                 "relation": relation})
        cx.execute("INSERT INTO lineage_edges(edge_id,world_id,src_kind,src_id,"
                   "dst_kind,dst_id,relation,claimed,created_ts,created_seq) "
                   "VALUES(?,?,?,?,?,?,?,?,?,?)",
                   (eid, world_id, src_kind, src_id, dst_kind, dst_id, relation,
                    claimed, now(), ev["event_seq"]))
        return eid

    def add_lineage_edge(self, world_id, src_kind, src_id, dst_kind, dst_id,
                         relation, *, client_id=None) -> str:
        with self.store.write() as cx:
            r = self._authorize_write(cx, world_id, client_id)
            return self._edge(cx, world_id, r["client_id"], src_kind, src_id,
                              dst_kind, dst_id, relation)

    # ================= artifacts + import (provenance) ==================
    def create_artifact(self, world_id: str, kind: str, data: bytes, *,
                        client_id: Optional[str] = None,
                        meta: Optional[dict] = None,
                        idem_key: Optional[str] = None,
                        expected_blob_hash: Optional[str] = None,
                        request_hash: Optional[str] = None) -> dict:
        """Store bytes as a content-addressed artifact.

        CONTENT-ID GATE (D-CIDGATE-1, 2026-09-04): pass expected_blob_hash to
        make the engine ENFORCE the content identity. The engine always computes
        the digest itself -- a client has never been able to assert a false one
        here -- but before this gate it had no way to be TOLD what the bytes were
        supposed to be, so corruption in transit or in a caller's own pipeline
        was stored as a perfectly valid artifact with an honest digest of the
        WRONG bytes (Harmonia A3). The check is one comparison and it belongs
        here, not re-implemented in every caller."""
        # meta is freeform USER metadata BY DESIGN -- except info_kind, which is
        # CONTROL configuration for the sharing machinery and must come from the
        # closed vocabulary (DFX-4: scientific config fails closed recursively).
        ik = (meta or {}).get("info_kind")
        if ik is not None and ik not in INFO_KINDS:
            raise ValidationError("unknown info_kind", info_kind=ik,
                                  allowed=sorted(INFO_KINDS))
        raw = data if isinstance(data, bytes) else str(data).encode()
        if expected_blob_hash is not None:
            actual = "sha256:" + hashlib.sha256(raw).hexdigest()
            claimed = expected_blob_hash.strip()
            if not claimed.startswith("sha256:"):
                claimed = "sha256:" + claimed
            if claimed.lower() != actual:
                raise ValidationError(
                    "content identity mismatch: the bytes received do not hash "
                    "to the asserted expected_blob_hash. Nothing was stored. "
                    "The bytes were corrupted or the wrong object was sent.",
                    world_id=world_id, expected=claimed, actual=actual,
                    received_bytes=len(raw))
        with self.store.write() as cx:
            r = self._authorize_write(cx, world_id, client_id)
            replay = self._idem_check(cx, r["client_id"], idem_key, request_hash)
            if replay is not None:
                return replay
            blob = self.store.put_blob(raw)
            aid = content_hash({"world": world_id, "kind": kind, "blob": blob,
                                "meta": meta or {}})
            ev = events.append(cx, world_id, "ARTIFACT_CREATED",
                               actor=r["client_id"],
                               refs={"artifact_id": aid}, artifacts=[blob])
            cx.execute(
                "INSERT OR IGNORE INTO artifacts(artifact_id,world_id,kind,"
                "blob_hash,meta,origin,created_ts,created_seq) "
                "VALUES(?,?,?,?,?, 'NATIVE',?,?)",
                (aid, world_id, kind, blob, json.dumps(meta or {}), now(),
                 ev["event_seq"]))
            out = {"artifact_id": aid, "blob_hash": blob, "origin": "NATIVE"}
            self._idem_record(cx, r["client_id"], idem_key, world_id,
                              "artifacts", request_hash, out)
            return out

    def get_artifact(self, world_id: str, artifact_id: str, *,
                     client_id: Optional[str] = None) -> dict:
        cx = self.store.read()
        self._authorize(cx, world_id, client_id)
        r = cx.execute("SELECT * FROM artifacts WHERE world_id=? AND "
                       "artifact_id=?", (world_id, artifact_id)).fetchone()
        if r is None:
            raise NotFound("artifact not in this world", artifact_id=artifact_id)
        return _artifact_dict(r)

    def get_artifact_content(self, world_id: str, artifact_id: str, *,
                             client_id: Optional[str] = None) -> dict:
        """F1 -- policy-gated CONTENT retrieval. Succeeds iff the artifact is
        epistemically VISIBLE to the requesting world: a local artifacts row for
        (world_id, artifact_id) exists AND the caller owns the world. Visibility
        is therefore native-to-this-world OR legally-imported-into-this-world;
        possession of an artifact id, knowledge of an origin hash, or access to
        some OTHER world confers nothing -- the lookup is scoped to the
        requesting world's own rows behind _authorize, and a miss is deny-by-
        default (NotFound, disclosing nothing). For an imported artifact the
        bytes ARE the source's (blob_hash was copied at import) and get_blob
        re-verifies the content hash on read, so returned content provably hashes
        to the recorded source identity. Retrieval never mutates the ledger (no
        availability transition occurs on a read; availability was fixed at
        native creation or import), consistent with GEN-2 read semantics."""
        cx = self.store.read()
        self._authorize(cx, world_id, client_id)   # 403 if not the caller's world
        r = cx.execute("SELECT * FROM artifacts WHERE world_id=? AND "
                       "artifact_id=?", (world_id, artifact_id)).fetchone()
        if r is None:
            raise NotFound("artifact not visible to this world",
                           artifact_id=artifact_id)
        content = self.store.get_blob(r["blob_hash"])   # verifies hash on read
        basis = {"visibility": "NATIVE"}
        if r["origin"] == "IMPORTED":
            imp = cx.execute("SELECT payload FROM events WHERE event_seq=? AND "
                             "world_id=?",
                             (r["import_seq"], world_id)).fetchone()
            basis = {"visibility": "IMPORTED",
                     **(json.loads(imp["payload"]) if imp else {})}
        import base64
        return {"world_id": world_id, "artifact_id": artifact_id,
                "origin": r["origin"], "source_world": r["source_world"],
                "source_artifact": r["source_artifact"],
                "source_hash": r["blob_hash"], "blob_hash": r["blob_hash"],
                "import_seq": r["import_seq"], "kind": r["kind"],
                "meta": json.loads(r["meta"]), "visibility_basis": basis,
                "content_b64": base64.b64encode(content).decode()}

    def knowledge_set(self, world_id: str, *, seq: Optional[int] = None,
                      client_id: Optional[str] = None) -> dict:
        """F10 -- the information-availability frontier, RECONSTRUCTED from the
        ledger (no separate state). Returns the artifact/information identities
        that were LEGALLY AVAILABLE to `world_id` at or before event `seq`
        (default: now). Availability is established by exactly two governed
        transitions -- native creation (ARTIFACT_CREATED) and legal import
        (ARTIFACT_IMPORTED) -- both already recorded with their event_seq, so
        `first_available_seq` is authoritative and monotonic. Fork-inherited
        artifacts become available at the child's WORLD_FORKED seq.

        This answers only 'could world W legally know X by seq N'. It does NOT
        assert the client READ X, USED X, or that X was causally decisive --
        those distinctions are preserved and out of scope.

        TRANSITIVELY correct across multi-level forks: a grandchild inherits its
        grandparent's frontier (reconstructed recursively from the parent's
        frontier AT the fork point), not just the immediate WORLD_FORKED list.
        Fail-CLOSED: an availability seq that is unknown (NULL) is EXCLUDED under
        a cutoff, never surfaced as if it existed early."""
        cx = self.store.read()
        self._authorize(cx, world_id, client_id)
        items = self._reconstruct_frontier(cx, world_id, seq)
        items.sort(key=lambda x: (x["first_available_seq"] is None,
                                  x["first_available_seq"] or 0))
        head = cx.execute("SELECT MAX(event_seq) m FROM events WHERE "
                          "world_id=?", (world_id,)).fetchone()["m"]
        return {"world_id": world_id, "as_of_seq": seq,
                "world_head_seq": head,
                "seq_axis": "global event_seq (same ordering as created_seq / "
                            "committed_seq); omit as_of_seq for 'now'",
                "available_count": len(items), "available": items,
                "note": "availability != read != used != causally responsible"}

    def _reconstruct_frontier(self, cx, world_id, cutoff):
        """Availability frontier of `world_id` at/<= global event_seq `cutoff`
        (None = now), reconstructed from the ledger and TRANSITIVE across forks.
        Fail-closed: unknown availability is excluded under a cutoff."""
        items, seen = [], set()
        for r in cx.execute("SELECT * FROM artifacts WHERE world_id=? ORDER BY "
                            "created_seq", (world_id,)).fetchall():
            avail = r["import_seq"] if r["origin"] == "IMPORTED" \
                else r["created_seq"]
            if avail is None:
                if cutoff is not None:            # fail-closed on unknown seq
                    continue
            elif cutoff is not None and avail > cutoff:
                continue
            items.append({
                "artifact_id": r["artifact_id"], "origin": r["origin"],
                "source_world": r["source_world"],
                "source_artifact": r["source_artifact"],
                "content_hash": r["blob_hash"], "first_available_seq": avail,
                "basis": "native_creation" if r["origin"] == "NATIVE"
                         else "legal_import"})
            seen.add(r["blob_hash"])
        # fork inheritance: everything available to the PARENT at the fork point
        # becomes available to this world at ITS fork seq -- recursively, so a
        # grandchild inherits the grandparent's frontier (not just the immediate
        # WORLD_FORKED list).
        w = cx.execute("SELECT parent_world_id, fork_point FROM worlds WHERE "
                       "world_id=?", (world_id,)).fetchone()
        if w is not None and w["parent_world_id"] is not None:
            fk = cx.execute("SELECT event_seq FROM events WHERE world_id=? AND "
                            "event_type='WORLD_FORKED'", (world_id,)).fetchone()
            fork_seq = fk["event_seq"] if fk else None
            if fork_seq is not None and (cutoff is None or fork_seq <= cutoff):
                pcut = cx.execute(
                    "SELECT event_seq FROM events WHERE world_id=? AND "
                    "world_index=?",
                    (w["parent_world_id"], int(w["fork_point"]))).fetchone()
                for it in self._reconstruct_frontier(
                        cx, w["parent_world_id"],
                        pcut["event_seq"] if pcut else None):
                    if it["content_hash"] in seen:
                        continue
                    seen.add(it["content_hash"])
                    items.append({
                        "artifact_id": None, "origin": "INHERITED",
                        "source_world": w["parent_world_id"],
                        "source_artifact": it.get("artifact_id"),
                        "content_hash": it["content_hash"],
                        "first_available_seq": fork_seq,
                        "basis": "fork_inheritance"})
        return items

    def _may_cross(self, dst_row, src_row, info_kind: str, *,
                   same_client: bool) -> bool:
        """Whether `info_kind` may cross from src world to dst world (section 13).

        The DESTINATION must accept the kind (its sharing policy admits it). For a
        CROSS-client import (experimenter B pulling from experimenter A) that is
        NOT sufficient: A must have consented, so we additionally require an
        explicit bilateral topology share -- both worlds in the SAME (non-null)
        topology_group AND the SOURCE world's own policy emits this kind. Within a
        single client's own program (same_client) the experimenter controls both
        ends, so only the destination gate + matching-group rule apply. ISOLATED
        emits and accepts nothing, so it forbids all crossing in either role."""
        if info_kind not in SHARING_POLICIES.get(dst_row["sharing_policy"],
                                                 frozenset()):
            return False
        dg, sg = dst_row["topology_group"], src_row["topology_group"]
        if same_client:
            return not (dg is not None and sg is not None and dg != sg)
        # cross-client: an explicit bilateral topology share is mandatory, and
        # the SOURCE world must itself emit this kind (A's own consent).
        if dg is None or sg is None or dg != sg:
            return False
        return info_kind in SHARING_POLICIES.get(src_row["sharing_policy"],
                                                 frozenset())

    def import_artifact(self, dst_world: str, src_world: str,
                        src_artifact_id: str, *,
                        client_id: Optional[str] = None) -> dict:
        """Explicit cross-world import. The imported artifact is recorded with
        permanent provenance (origin=IMPORTED, source world/artifact/hash) so it
        can NEVER be mistaken for something independently discovered in the
        destination (I5, section 14, T10). Governed by the destination's sharing
        policy (T14)."""
        with self.store.write() as cx:
            dst = self._authorize_write(cx, dst_world, client_id)   # must own dest
            src = self._world_row(cx, src_world)
            same_client = (client_id is None
                           or src["client_id"] == client_id)
            # A CROSS-client import requires an explicit bilateral topology
            # share. Deny (uniformly, BEFORE the artifact is looked up)
            # otherwise, so a non-owner can neither pull a foreign artifact's
            # bytes nor probe which artifact ids exist in another
            # experimenter's world (I5).
            if not same_client:
                dg, sg = dst["topology_group"], src["topology_group"]
                if dg is None or sg is None or dg != sg:
                    raise AccessDenied(
                        "cross-world import requires a shared topology group",
                        dst_world=dst_world, src_world=src_world)
                # H5: matching STRINGS are not consent. The shared group must be
                # a server-issued, unguessable REGISTERED capability -- two
                # clients hold the same group id only by deliberate transfer.
                if cx.execute("SELECT 1 FROM topology_groups WHERE group_id=?",
                              (sg,)).fetchone() is None:
                    raise AccessDenied(
                        "cross-world import requires a REGISTERED topology "
                        "group (create one via create_topology_group and share "
                        "its id deliberately)",
                        dst_world=dst_world, src_world=src_world)
            srow = cx.execute("SELECT * FROM artifacts WHERE world_id=? AND "
                              "artifact_id=?",
                              (src_world, src_artifact_id)).fetchone()
            if srow is None:
                raise NotFound("source artifact not found",
                               src_artifact_id=src_artifact_id)
            # H6: no TRANSITIVE re-export across clients. A cross-client import
            # must draw from the artifact's ORIGIN (a NATIVE row); an IMPORTED
            # copy held by an intermediary cannot be re-exported to a third
            # client -- A sharing with B never implicitly authorizes B->C.
            if not same_client and srow["origin"] != "NATIVE":
                raise AccessDenied(
                    "cross-client import of an IMPORTED artifact is not "
                    "allowed; import from the origin world (redistribution "
                    "requires the original owner's own share)",
                    dst_world=dst_world, src_world=src_world)
            # The information KIND the artifact represents governs whether policy
            # lets it cross. F2: kinds are a closed ontology
            # {artifact, failure, hypothesis, observation, success}; "success" is
            # FIRST-CLASS (not a synonym for "artifact"), so a producer that
            # wants SUCCESSES_ONLY sharing tags meta.info_kind="success". Read the
            # specific kind (default "artifact" when meta declares none).
            info_kind = json.loads(srow["meta"]).get("info_kind", "artifact")
            if not self._may_cross(dst, src, info_kind, same_client=same_client):
                raise IsolationViolation(
                    "sharing policy forbids importing this information kind",
                    dst_world=dst_world, src_world=src_world, info_kind=info_kind,
                    dst_policy=dst["sharing_policy"])
            new_aid = content_hash({"import_into": dst_world,
                                    "source": src_artifact_id,
                                    "src_world": src_world})
            ev = events.append(cx, dst_world, "ARTIFACT_IMPORTED",
                               actor=dst["client_id"],
                               refs={"artifact_id": new_aid,
                                     "source_world": src_world,
                                     "source_artifact": src_artifact_id,
                                     "source_hash": srow["blob_hash"]},
                               # policy basis recorded so visibility is auditable
                               # and reconstructable (F1 provenance, F10 basis)
                               payload={"info_kind": info_kind,
                                        "same_client": same_client,
                                        "dst_policy": dst["sharing_policy"],
                                        "src_policy": src["sharing_policy"],
                                        "topology_group": dst["topology_group"]},
                               artifacts=[srow["blob_hash"]])
            cx.execute(
                "INSERT OR IGNORE INTO artifacts(artifact_id,world_id,kind,"
                "blob_hash,meta,origin,source_world,source_artifact,import_seq,"
                "created_ts,created_seq) VALUES(?,?,?,?,?, 'IMPORTED',?,?,?,?,?)",
                (new_aid, dst_world, srow["kind"], srow["blob_hash"],
                 srow["meta"], src_world, src_artifact_id, ev["event_seq"],
                 now(), ev["event_seq"]))
            return {"artifact_id": new_aid, "origin": "IMPORTED",
                    "source_world": src_world, "source_artifact": src_artifact_id,
                    "source_hash": srow["blob_hash"]}

    # ================= checkpoint + fork ================================
    def checkpoint(self, world_id: str, *, client_id: Optional[str] = None,
                   meta: Optional[dict] = None) -> dict:
        ckid = new_id("checkpoint")
        with self.store.write() as cx:
            r = self._authorize(cx, world_id, client_id)
            idx = int(r["next_index"]) - 1     # last committed event index
            head = r["head_hash"] or ""
            snap = self._state_snapshot(cx, world_id)
            state_hash = content_hash(snap)
            cx.execute(
                "INSERT INTO checkpoints(checkpoint_id,world_id,world_index,"
                "head_hash,state_hash,meta,created_ts) VALUES(?,?,?,?,?,?,?)",
                (ckid, world_id, idx, head, state_hash,
                 json.dumps(meta or {}), now()))
            events.append(cx, world_id, "CHECKPOINT_CREATED",
                          actor=r["client_id"],
                          refs={"checkpoint_id": ckid},
                          payload={"world_index": idx, "state_hash": state_hash})
        return {"checkpoint_id": ckid, "world_index": idx, "head_hash": head,
                "state_hash": state_hash}

    def _state_snapshot(self, cx, world_id: str) -> dict:
        def c(t):
            return cx.execute(f"SELECT COUNT(*) n FROM {t} WHERE world_id=?",
                              (world_id,)).fetchone()["n"]
        return {"hypotheses": c("hypotheses"), "predictions": c("predictions"),
                "experiments": c("experiments"), "observations": c("observations"),
                "failures": c("failures"), "artifacts": c("artifacts"),
                "head": self._world_row(cx, world_id)["head_hash"]}

    def fork(self, world_id: str, checkpoint_id: str, children: list, *,
             client_id: Optional[str] = None) -> list:
        """Fork a world at a checkpoint into N children. Each child SHARES the
        parent's immutable event prefix up to the checkpoint BY REFERENCE (not a
        copy), then diverges independently. Parent rows are never written by a
        child and vice versa, so they cannot mutate one another (I5, section 5,
        T9). Inherited artifact hashes and per-child interventions are recorded
        in each child's WORLD_FORKED event.

        NOTE: fork inherits EVIDENCE (the event history) by reference. Relational
        research-state is per-child (empty at fork); identical starting
        conditions for a counterfactual are established by identical seed_root +
        identical initial configuration, which keeps mutation-isolation
        structural rather than copy-based.
        """
        out = []
        with self.store.write() as cx:
            parent = self._authorize(cx, world_id, client_id)
            ck = cx.execute("SELECT * FROM checkpoints WHERE checkpoint_id=? "
                            "AND world_id=?",
                            (checkpoint_id, world_id)).fetchone()
            if ck is None:
                raise NotFound("checkpoint not in this world",
                               checkpoint_id=checkpoint_id)
            fork_point = int(ck["world_index"])
            fork_head = ck["head_hash"]
            inherited_hashes = [r["blob_hash"] for r in cx.execute(
                "SELECT blob_hash FROM artifacts WHERE world_id=? AND "
                "created_seq<=(SELECT event_seq FROM events WHERE world_id=? AND "
                "world_index=?)", (world_id, world_id, fork_point)).fetchall()]
            plimits = cx.execute("SELECT limits FROM budgets WHERE world_id=?",
                                 (world_id,)).fetchone()
            for spec in children:
                cwid = new_id("world")
                pol = spec.get("sharing_policy", parent["sharing_policy"])
                if pol not in SHARING_POLICIES:
                    raise ValidationError("unknown sharing policy",
                                          sharing_policy=pol)
                sroot = spec.get("seed_root", parent["seed_root"])
                # H3: a fork INHERITS its parent's budget_root, so the whole
                # lineage draws from ONE authoritative campaign budget --
                # forking cannot mint fresh scientific budget. The child's own
                # budgets row (limits copied, consumed reset) is a LOCAL safety
                # cap only; authoritative consumption debits the root too.
                cx.execute(
                    "INSERT INTO worlds(world_id,session_id,client_id,name,"
                    "state,parent_world_id,fork_point,sharing_policy,"
                    "topology_group,seed_root,budget_root,next_index,"
                    "head_hash,created_ts) "
                    "VALUES(?,?,?,?,'CREATED',?,?,?,?,?,?,?,?,?)",
                    (cwid, parent["session_id"], parent["client_id"],
                     spec.get("name", "fork"), world_id, fork_point, pol,
                     spec.get("topology_group", parent["topology_group"]),
                     int(sroot), parent["budget_root"] or world_id,
                     fork_point + 1, fork_head, now()))
                cx.execute("INSERT INTO budgets(world_id,limits,consumed,"
                           "updated_ts) VALUES(?,?,?,?)",
                           (cwid, plimits["limits"], json.dumps({}), now()))
                # v6 NO_EFFECTIVE_INTERVENTION. Computed BEFORE the event so
                # the finding is sealed in the chain, not merely returned.
                findings = []
                if self.science_profile != "off":
                    findings = _intervention_findings(
                        parent, spec,
                        {"seed_root": int(sroot), "sharing_policy": pol,
                         "topology_group": spec.get(
                             "topology_group", parent["topology_group"])})
                    contradictions = [f for f in findings
                                      if f["code"] in _FORK_CONTRADICTIONS]
                    finding = contradictions[0] if contradictions else None
                    if finding is not None \
                            and (spec.get("intervention_effective") is True
                                 or self.science_profile == "strict"):
                        # Warn by default; REJECT when the fork's own manifest
                        # declares the intervention effective. The engine is
                        # not overruling a scientist -- it is refusing to
                        # record a fork whose declaration contradicts its own
                        # arithmetic.
                        raise ValidationError(
                            "fork declares an effective intervention that "
                            "changed nothing: " + finding["message"],
                            world_id=world_id, **{k: v for k, v in
                                                  finding.items()
                                                  if k != "message"})
                fpayload = {"fork_point": fork_point,
                            "parent_head": fork_head,
                            "interventions": spec.get("interventions", {})}
                if findings:
                    # `findings` is canonical. `finding` is kept as the first
                    # entry because two WORLD_FORKED events were sealed with
                    # that key before this became a list, and a sealed ledger
                    # is not rewritten to tidy a shape.
                    fpayload["findings"] = findings
                    fpayload["finding"] = findings[0]
                # the child's FIRST event chains onto the parent's fork head
                events.append(cx, cwid, "WORLD_FORKED", actor=parent["client_id"],
                              refs={"parent_world": world_id,
                                    "checkpoint_id": checkpoint_id},
                              artifacts=inherited_hashes,
                              payload=fpayload)
                child = self.get_world(cwid, parent["client_id"])
                if self.science_profile != "off":
                    child["science"] = {"profile_findings": findings}
                out.append(child)
        return out

    # ================= v6 scientific provenance =========================
    #
    # ONE rule governs everything in this section: the engine compares HASHES,
    # COUNTS distinct things, and checks CONTAINMENT of declared sets. It never
    # computes a variance, fits a model, chooses an estimator, or judges whether
    # a design was adequate. Where an answer would need statistical
    # interpretation the engine records the DECLARATION and the PROVENANCE and
    # stops -- the scientist keeps the science.
    #
    # Every check here is graded by ONE flag, --science-profile:
    #   off    -- not computed, not recorded, not reported. A true control arm:
    #             the engine behaves exactly as v5 did.
    #   warn   -- computed and reported (in the response AND sealed in the
    #             event), never blocking. The default.
    #   strict -- the same findings, but a finding that contradicts a sealed
    #             declaration fails the call.
    # warn and strict agree on every FACT and differ only in CONSEQUENCE, which
    # is what makes an off/warn/strict A/B a fair test rather than two engines.

    def _sci(self) -> str:
        return self.science_profile

    @staticmethod
    def _member_scope(cx, member_kind: str, member_id: str, client_id: str):
        """Resolve a family member to (world_id, owning_client), or None.

        A member owned by a DIFFERENT client resolves to None rather than
        raising: a family is cross-world by construction, and an engine that
        answered "access denied" here would turn family membership into an
        existence oracle for another client's substrate (I5)."""
        if member_kind == "world":
            r = cx.execute("SELECT world_id, client_id FROM worlds WHERE "
                           "world_id=?", (member_id,)).fetchone()
            if r is None or r["client_id"] != client_id:
                return None
            return r["world_id"]
        if member_kind in ("experiment", "analysis"):
            r = cx.execute(
                "SELECT e.world_id AS world_id, w.client_id AS client_id, "
                "e.source_set_hash AS ssh FROM experiments e "
                "JOIN worlds w ON w.world_id = e.world_id WHERE e.exp_id=?",
                (member_id,)).fetchone()
            if r is None or r["client_id"] != client_id:
                return None
            if member_kind == "analysis" and r["ssh"] is None:
                raise ValidationError(
                    "member_kind='analysis' but this experiment carries no "
                    "source_set_hash; an analysis is an experiment REGISTERED "
                    "with a source set (see create_experiment source_set)",
                    exp_id=member_id)
            return r["world_id"]
        if member_kind == "claim":
            r = cx.execute("SELECT client_id FROM claims WHERE claim_id=?",
                           (member_id,)).fetchone()
            if r is None or r["client_id"] != client_id:
                return None
            return None          # a claim belongs to no single world (v6)
        raise ValidationError("unknown member_kind", member_kind=member_kind,
                              allowed=sorted(FAMILY_MEMBER_KINDS))

    def create_family(self, *, client_id: str, kind: str, manifest: dict,
                      name: Optional[str] = None) -> dict:
        """Create a CROSS-WORLD scientific container and seal its manifest.

        This is the first container in the engine that is not world-scoped, and
        that is the whole reason it exists: a campaign, an analysis family, a
        comparison or a selection spans worlds BY DEFINITION, so no amount of
        per-world lineage can express one. Without it, "the survivor of twelve"
        and "the only one I ran" are the same record.

        The manifest is FREEFORM and OPAQUE -- the engine hashes it, never reads
        it -- with exactly one convention it does read: an integer under
        `planned_members` (or `planned_experiments`) is compared against the
        members actually recorded, which is counting, not judgement.

        manifest_hash is sealed at creation and never rewritten. A family whose
        declared extent grows after the results are in is precisely the failure
        this makes visible."""
        if kind not in FAMILY_KINDS:
            raise ValidationError("unknown family kind", kind=kind,
                                  allowed=sorted(FAMILY_KINDS))
        if not isinstance(manifest, dict):
            raise ValidationError("manifest must be an object")
        fid = new_id("family")
        mh = content_hash(manifest)
        ts = now()
        with self.store.write() as cx:
            if cx.execute("SELECT 1 FROM clients WHERE client_id=?",
                          (client_id,)).fetchone() is None:
                raise NotFound("unknown client", client_id=client_id)
            body = dict(manifest)
            if name is not None:
                body = {**manifest, "_name": name}
            cx.execute("INSERT INTO families(family_id,client_id,kind,manifest,"
                       "manifest_hash,state,created_ts) "
                       "VALUES(?,?,?,?,?,'OPEN',?)",
                       (fid, client_id, kind, json.dumps(body), mh, ts))
            events.append_foundry(cx, "FAMILY_CREATED", actor=client_id,
                                  scope_kind="family", scope_id=fid,
                                  payload={"kind": kind, "manifest_hash": mh,
                                           "engine_source_hash":
                                               release.ENGINE_SOURCE_HASH})
        return {"family_id": fid, "kind": kind, "state": "OPEN",
                "manifest_hash": mh, "created_ts": ts}

    def _family_row(self, cx, family_id: str, client_id: Optional[str]):
        r = cx.execute("SELECT * FROM families WHERE family_id=?",
                       (family_id,)).fetchone()
        if r is None:
            raise NotFound("unknown family", family_id=family_id)
        if client_id is not None and r["client_id"] != client_id:
            raise AccessDenied("family belongs to another client",
                               family_id=family_id)
        return r

    def add_family_member(self, family_id: str, *, member_kind: str,
                          member_id: str, role: Optional[str] = None,
                          arm: Optional[str] = None,
                          client_id: Optional[str] = None) -> dict:
        """Attach one member. Idempotent on (family, kind, id): re-adding with
        the SAME role is a no-op replay; re-adding with a DIFFERENT role is a
        409, because a member silently moving from `alternative` to `selected`
        after the fact is exactly the rewrite this table exists to prevent."""
        if member_kind not in FAMILY_MEMBER_KINDS:
            raise ValidationError("unknown member_kind",
                                  member_kind=member_kind,
                                  allowed=sorted(FAMILY_MEMBER_KINDS))
        if role is not None and role not in FAMILY_ROLES:
            raise ValidationError("unknown role", role=role,
                                  allowed=sorted(FAMILY_ROLES))
        ts = now()
        with self.store.write() as cx:
            fam = self._family_row(cx, family_id, client_id)
            if fam["state"] != "OPEN":
                raise InvalidTransition("family is CLOSED; membership is sealed",
                                        family_id=family_id)
            owner = fam["client_id"]
            # v7 ARM RULING: the manifest may seal the arm VOCABULARY, and an
            # arm outside it was never part of this design.
            declared = json.loads(fam["manifest"]).get("arms")
            if arm is not None and isinstance(declared, list) and declared \
                    and arm not in declared:
                raise ValidationError(
                    "arm is not one the family's sealed manifest declares",
                    family_id=family_id, arm=arm, declared_arms=declared)
            prior = cx.execute(
                "SELECT role, arm FROM family_members WHERE family_id=? AND "
                "member_kind=? AND member_id=?",
                (family_id, member_kind, member_id)).fetchone()
            if prior is not None:
                if prior["role"] == role and prior["arm"] == arm:
                    return {"family_id": family_id, "member_kind": member_kind,
                            "member_id": member_id, "role": role, "arm": arm,
                            "already_member": True}
                # REASSIGNMENT AFTER COMMITMENT IS REFUSED. A member whose arm
                # can move once the results are in is the whole failure this
                # binding exists to prevent.
                raise ConflictError(
                    "member already in this family under a DIFFERENT role or "
                    "arm; membership is append-only",
                    family_id=family_id, member_id=member_id,
                    recorded_role=prior["role"], submitted_role=role,
                    recorded_arm=prior["arm"], submitted_arm=arm)
            wid = self._member_scope(cx, member_kind, member_id, owner)
            if wid is None and member_kind != "claim":
                raise NotFound(
                    "member not found in this client's substrate",
                    member_kind=member_kind, member_id=member_id)
            cx.execute("INSERT INTO family_members(family_id,member_kind,"
                       "member_id,world_id,role,arm,created_ts) "
                       "VALUES(?,?,?,?,?,?,?)",
                       (family_id, member_kind, member_id, wid, role, arm, ts))
            events.append_foundry(cx, "FAMILY_MEMBER_ADDED", actor=owner,
                                  scope_kind="family", scope_id=family_id,
                                  payload={"member_kind": member_kind,
                                           "member_id": member_id,
                                           "world_id": wid, "role": role,
                                           "arm": arm})
        return {"family_id": family_id, "member_kind": member_kind,
                "member_id": member_id, "world_id": wid, "role": role,
                "arm": arm, "already_member": False}

    def close_family(self, family_id: str, *,
                     client_id: Optional[str] = None) -> dict:
        with self.store.write() as cx:
            fam = self._family_row(cx, family_id, client_id)
            if fam["state"] == "CLOSED":
                return {"family_id": family_id, "state": "CLOSED",
                        "already_closed": True}
            cx.execute("UPDATE families SET state='CLOSED' WHERE family_id=?",
                       (family_id,))
            events.append_foundry(cx, "FAMILY_CLOSED", actor=fam["client_id"],
                                  scope_kind="family", scope_id=family_id,
                                  payload={})
        return {"family_id": family_id, "state": "CLOSED",
                "already_closed": False}

    def get_family(self, family_id: str, *,
                   client_id: Optional[str] = None) -> dict:
        """The family plus its provenance census.

        `selection_visible` is the property the whole table was added for: a
        family that records BOTH a selected member and at least one alternative
        makes best-of-N legible. One selected member and no alternatives is not
        a lie, but it is not a selection family either, and the engine says so
        rather than letting the reader assume."""
        cx = self.store.read()
        fam = self._family_row(cx, family_id, client_id)
        rows = cx.execute(
            "SELECT member_kind, member_id, world_id, role, arm, created_ts "
            "FROM family_members WHERE family_id=? ORDER BY created_ts, "
            "member_id", (family_id,)).fetchall()
        members = [{"member_kind": r["member_kind"], "member_id": r["member_id"],
                    "world_id": r["world_id"], "role": r["role"],
                    "arm": r["arm"], "created_ts": r["created_ts"]}
                   for r in rows]
        by_role: dict = {}
        by_kind: dict = {}
        for m in members:
            by_role[m["role"] or "unspecified"] = \
                by_role.get(m["role"] or "unspecified", 0) + 1
            by_kind[m["member_kind"]] = by_kind.get(m["member_kind"], 0) + 1
        worlds = {m["world_id"] for m in members if m["world_id"]}
        manifest = json.loads(fam["manifest"])
        out = {"family_id": family_id, "client_id": fam["client_id"],
               "kind": fam["kind"], "state": fam["state"],
               "manifest": manifest, "manifest_hash": fam["manifest_hash"],
               "created_ts": fam["created_ts"],
               "members": members, "member_count": len(members),
               "by_role": by_role, "by_kind": by_kind,
               "worlds_spanned": len(worlds),
               "selection_visible": by_role.get("selected", 0) >= 1
                                    and by_role.get("alternative", 0) >= 1}
        out["arms"] = self._family_arms(cx, manifest, rows)
        if self._sci() != "off":
            out["science"] = self._family_findings(manifest, members, by_role)
        return out

    @staticmethod
    def _family_arms(cx, manifest: dict, rows) -> dict:
        """Arm structure, from the sealed DESIGN.

        ARM RULING (2026-09-06): execution parameters are sealed by spec_hash;
        family and arm assignment are sealed SEPARATELY, in the append-only
        member record and its FAMILY_MEMBER_ADDED event. Keeping the arm out of
        the execution spec is what lets two arms carry an IDENTICAL execution
        hash -- what was RUN and what ROLE it played are different facts, and
        folding the label into the spec would make identical executions hash
        differently and destroy the very comparison the design exists for.

        The manifest may seal the arm VOCABULARY (`arms: ["A","B"]`), so an arm
        outside the declared design is refused at membership.

        `spec_conflicts` is the honest counterpart: if an execution spec ALSO
        carries the manifest's arm_key with a different value, someone has
        smuggled design into execution and the two disagree. Comparing two
        declared strings is comparison, not interpretation."""
        counts, unassigned, conflicts = {}, 0, []
        key = manifest.get("arm_key", "arm")
        for r in rows:
            arm = r["arm"]
            if arm is None:
                unassigned += 1
            else:
                counts[arm] = counts.get(arm, 0) + 1
            if isinstance(key, str) and key and \
                    r["member_kind"] in ("experiment", "analysis"):
                ex = cx.execute("SELECT spec FROM experiments WHERE exp_id=?",
                                (r["member_id"],)).fetchone()
                if ex is not None:
                    try:
                        found, val = _dig(json.loads(ex["spec"]), key)
                    except (TypeError, ValueError):
                        found, val = False, None
                    if found and str(val) != str(arm):
                        conflicts.append({"member_id": r["member_id"],
                                          "sealed_arm": arm,
                                          "spec_says": str(val)})
        return {"counts": dict(sorted(counts.items())),
                "distinct_arms": len(counts),
                "unassigned": unassigned,
                "declared_arms": manifest.get("arms"),
                "arm_key_watched": key if isinstance(key, str) else None,
                "spec_conflicts": conflicts,
                "balanced": (len(set(counts.values())) == 1
                             if len(counts) > 1 else None)}

    @staticmethod
    def _family_findings(manifest: dict, members: list, by_role: dict) -> dict:
        """Declared extent vs recorded extent. Pure counting."""
        findings = []
        planned = manifest.get("planned_members",
                               manifest.get("planned_experiments"))
        if isinstance(planned, bool) or not isinstance(planned, int):
            planned = None
        if planned is not None:
            recorded = len(members)
            if recorded != planned:
                findings.append({
                    "code": "FAMILY_EXTENT_DIVERGENCE",
                    "declared_members": planned, "recorded_members": recorded,
                    "message": "the manifest declared an extent the recorded "
                               "membership does not match"})
        if by_role.get("selected", 0) > 1:
            findings.append({
                "code": "MULTIPLE_SELECTED",
                "selected": by_role["selected"],
                "message": "more than one member is marked selected; a "
                           "best-of-N family has exactly one survivor"})
        if by_role.get("selected", 0) == 1 and by_role.get("alternative", 0) == 0:
            findings.append({
                "code": "SELECTION_WITHOUT_ALTERNATIVES",
                "message": "a selected member with no recorded alternatives: "
                           "the selection is asserted but not visible"})
        return {"profile_findings": findings,
                "declared_members": planned,
                "recorded_members": len(members)}

    def list_families(self, *, client_id: Optional[str] = None,
                      kind: Optional[str] = None, limit: int = 100) -> list:
        q = "SELECT family_id, client_id, kind, state, manifest_hash, " \
            "created_ts FROM families WHERE 1=1"
        args: list = []
        if client_id is not None:
            q += " AND client_id=?"
            args.append(client_id)
        if kind is not None:
            q += " AND kind=?"
            args.append(kind)
        q += " ORDER BY created_ts DESC LIMIT ?"
        args.append(int(limit))
        return [dict(r) for r in self.store.read().execute(q, args).fetchall()]

    # ---- claims -----------------------------------------------------------

    def create_claim(self, *, client_id: str, estimand: str, status: str,
                     family_id: Optional[str] = None,
                     analysis_exp_id: Optional[str] = None,
                     relevance_floor: Optional[Any] = None,
                     replication: Optional[dict] = None,
                     transport_domain: Optional[Any] = None) -> dict:
        """Record a scientific CLAIM: the assertion, not the data.

        A claim is deliberately NOT a world record. It cites an analysis, which
        cites observations, which live in worlds -- so binding it to one world
        would force every multi-world conclusion to pick a world to lie in.

        SUCCESSFUL_NEGATIVE exists because "the effect is bounded below a
        declared relevance floor" is a POSITIVE result. Today it can only be
        stored as SURVIVED (ambiguous with "the hypothesis stood") or
        INCONCLUSIVE (which destroys exactly the information that makes it
        valuable). The engine stores the conclusion the experimenter reached;
        it does not judge whether their equivalence test was valid. It enforces
        exactly one thing, in every profile: SUCCESSFUL_NEGATIVE without a
        declared relevance_floor is incoherent, because the claim is ABOUT the
        floor.

        `replication` is COMPOSITIONAL and never an ordinal. The L0-L4 and L1-L6
        ladders proposed two loops apart were on different axes; encoding either
        as a rank would hard-code a taxonomy that has already moved once. A dict
        of independent, individually-checkable dimensions survives the taxonomy
        changing, and any ladder anyone prefers can be derived from it later."""
        if status not in CLAIM_STATUSES:
            raise ValidationError("unknown claim status", status=status,
                                  allowed=sorted(CLAIM_STATUSES))
        if status == "RETRACTED":
            raise ValidationError(
                "a claim is RETRACTED by retract_claim, never born retracted")
        if not isinstance(estimand, str) or not estimand.strip():
            raise ValidationError("estimand must be a non-empty string")
        if status == "SUCCESSFUL_NEGATIVE" and relevance_floor is None:
            raise ValidationError(
                "SUCCESSFUL_NEGATIVE requires a declared relevance_floor: the "
                "claim is that the effect is bounded BELOW something, and "
                "without the bound there is no claim",
                status=status)
        rep = _normalize_replication(replication)
        cid_ = new_id("claim")
        ts = now()
        findings: list = []
        with self.store.write() as cx:
            if cx.execute("SELECT 1 FROM clients WHERE client_id=?",
                          (client_id,)).fetchone() is None:
                raise NotFound("unknown client", client_id=client_id)
            if family_id is not None:
                self._family_row(cx, family_id, client_id)
            awid = None
            if analysis_exp_id is not None:
                a = cx.execute(
                    "SELECT e.world_id AS world_id, e.spec AS spec, "
                    "e.source_set_hash AS ssh, w.client_id AS client_id "
                    "FROM experiments e JOIN worlds w ON w.world_id=e.world_id "
                    "WHERE e.exp_id=?", (analysis_exp_id,)).fetchone()
                if a is None or a["client_id"] != client_id:
                    raise NotFound("unknown analysis experiment",
                                   analysis_exp_id=analysis_exp_id)
                awid = a["world_id"]
                if self._sci() != "off":
                    if a["ssh"] is None:
                        findings.append({
                            "code": "CLAIM_CITES_NON_ANALYSIS",
                            "analysis_exp_id": analysis_exp_id,
                            "message": "the cited experiment declares no "
                                       "source set, so the claim's evidentiary "
                                       "base is not recorded"})
                    else:
                        # D-CLAIM-2 (2026-09-06). Having a source set is not
                        # the same as having a source set the engine could
                        # RESOLVE. An analysis whose sealed verification
                        # recorded verified_n=0, or a declared_n the engine's
                        # own count contradicts, used to produce a perfectly
                        # clean claim -- the strongest-looking output in the
                        # system resting on evidence the engine had already
                        # written down as unresolvable.
                        #
                        # Comparing two sealed integers is counting, not
                        # statistics, and it closes the path a PROGRAMMATIC
                        # producer walks by default: sources drawn from another
                        # client's worlds resolve to `unresolved` (the
                        # anti-oracle rule in _verify_units), so a cross-tenant
                        # analysis silently counts nothing at all.
                        findings.extend(_analysis_verification_findings(
                            cx, a["world_id"], analysis_exp_id))
                    findings.extend(_transport_findings(
                        transport_domain, json.loads(a["spec"])))
            if self._sci() != "off" and status == "SUPPORTED" and not rep:
                findings.append({
                    "code": "NO_REPLICATION_DECLARED",
                    "message": "a SUPPORTED claim declares no replication "
                               "dimensions; the engine records this and "
                               "enforces nothing"})
            if self._sci() == "strict":
                blocking = [f for f in findings
                            if f["code"] in _STRICT_BLOCKING_CLAIM]
                if blocking:
                    raise ValidationError(
                        "science-profile=strict: claim contradicts its own "
                        "declarations", findings=blocking)
            body = {"estimand": estimand, "status": status,
                    "family_id": family_id, "analysis_exp_id": analysis_exp_id,
                    "relevance_floor": relevance_floor, "replication": rep,
                    "transport_domain": transport_domain}
            ch = content_hash(body)
            cx.execute(
                "INSERT INTO claims(claim_id,client_id,family_id,"
                "analysis_exp_id,analysis_world_id,estimand,status,"
                "relevance_floor,replication,transport_domain,content_hash,"
                "created_ts) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                (cid_, client_id, family_id, analysis_exp_id, awid, estimand,
                 status,
                 None if relevance_floor is None else json.dumps(relevance_floor),
                 json.dumps(rep),
                 None if transport_domain is None else json.dumps(transport_domain),
                 ch, ts))
            events.append_foundry(cx, "CLAIM_RECORDED", actor=client_id,
                                  scope_kind="claim", scope_id=cid_,
                                  payload={"status": status,
                                           "family_id": family_id,
                                           "analysis_exp_id": analysis_exp_id,
                                           "content_hash": ch,
                                           "findings": findings,
                                           "engine_source_hash":
                                               release.ENGINE_SOURCE_HASH})
        out = {"claim_id": cid_, "status": status, "content_hash": ch,
               "family_id": family_id, "analysis_exp_id": analysis_exp_id,
               "analysis_world_id": awid, "replication": rep,
               "created_ts": ts}
        if self._sci() != "off":
            out["science"] = {"profile_findings": findings}
        return out

    def get_claim(self, claim_id: str, *,
                  client_id: Optional[str] = None) -> dict:
        """D-CLAIM-3 (2026-09-06): the findings are READABLE, not write-once.

        Under science_profile=warn nothing blocks, so the findings ARE the
        product of recording a claim. They were sealed into CLAIM_RECORDED and
        returned once from the POST -- and no route read them back, so a
        programmatic producer that did not parse and persist the creation
        response lost them permanently. Families recompute their science block
        on read and analyses read their sealed verification back; claims were
        the odd one out."""
        cx = self.store.read()
        r = cx.execute("SELECT * FROM claims WHERE claim_id=?",
                       (claim_id,)).fetchone()
        if r is None:
            raise NotFound("unknown claim", claim_id=claim_id)
        if client_id is not None and r["client_id"] != client_id:
            raise AccessDenied("claim belongs to another client",
                               claim_id=claim_id)
        out = _claim_dict(r)
        if self._sci() != "off":
            ev = cx.execute(
                "SELECT payload FROM foundry_events WHERE event_type="
                "'CLAIM_RECORDED' AND scope_kind='claim' AND scope_id=? "
                "ORDER BY seq DESC LIMIT 1", (claim_id,)).fetchone()
            sealed = {}
            if ev is not None:
                try:
                    sealed = json.loads(ev["payload"])
                except (TypeError, ValueError):
                    sealed = {}
            out["science"] = {
                "profile_findings": sealed.get("findings", []),
                "sealed_at_creation": ev is not None,
                "engine_source_hash": sealed.get("engine_source_hash")}
        return out

    def list_claims(self, *, client_id: Optional[str] = None,
                    family_id: Optional[str] = None,
                    status: Optional[str] = None, limit: int = 100) -> list:
        q, args = "SELECT * FROM claims WHERE 1=1", []
        if client_id is not None:
            q += " AND client_id=?"
            args.append(client_id)
        if family_id is not None:
            q += " AND family_id=?"
            args.append(family_id)
        if status is not None:
            q += " AND status=?"
            args.append(status)
        q += " ORDER BY created_ts DESC LIMIT ?"
        args.append(int(limit))
        return [_claim_dict(r)
                for r in self.store.read().execute(q, args).fetchall()]

    def retract_claim(self, claim_id: str, *, reason: str,
                      client_id: Optional[str] = None) -> dict:
        """RETRACTED is a transition, never an origin state, and the original
        content_hash is preserved: a retraction records that a claim was made
        and withdrawn, which is a different fact from the claim never existing."""
        if not isinstance(reason, str) or not reason.strip():
            raise ValidationError("a retraction requires a reason")
        with self.store.write() as cx:
            r = cx.execute("SELECT * FROM claims WHERE claim_id=?",
                           (claim_id,)).fetchone()
            if r is None:
                raise NotFound("unknown claim", claim_id=claim_id)
            if client_id is not None and r["client_id"] != client_id:
                raise AccessDenied("claim belongs to another client",
                                   claim_id=claim_id)
            if r["status"] == "RETRACTED":
                return _claim_dict(r)
            cx.execute("UPDATE claims SET status='RETRACTED' WHERE claim_id=?",
                       (claim_id,))
            events.append_foundry(cx, "CLAIM_RETRACTED", actor=r["client_id"],
                                  scope_kind="claim", scope_id=claim_id,
                                  payload={"reason": reason[:500],
                                           "prior_status": r["status"],
                                           "content_hash": r["content_hash"]})
            return _claim_dict(cx.execute(
                "SELECT * FROM claims WHERE claim_id=?", (claim_id,)).fetchone())

    # ---- analysis (an experiment with a declared source set) ---------------

    def _verify_units(self, cx, client_id: str, unit: str,
                      source_set: list) -> dict:
        """COUNT the distinct units under a declared key. Counting, not
        statistics -- and it is the difference between n=128 and n=8 when 128
        observations come from 8 worlds.

        A source owned by another client resolves to `unresolved` rather than
        raising, for the same isolation reason as _member_scope. That has a
        useful side effect: a cross-client analysis silently undercounts, and
        the declared-vs-verified check then makes the undercount visible."""
        if unit not in UNITS_OF_ANALYSIS:
            raise ValidationError("unknown unit_of_analysis", unit=unit,
                                  allowed=sorted(UNITS_OF_ANALYSIS))
        units, unresolved = set(), 0
        for sid in source_set:
            if not isinstance(sid, str):
                unresolved += 1
                continue
            row = None
            if sid.startswith("obs_"):
                row = cx.execute(
                    "SELECT o.world_id AS world_id, o.exp_id AS exp_id, "
                    "o.obs_id AS obs_id, w.client_id AS client_id, "
                    "w.seed_root AS seed_root, w.topology_group AS tg "
                    "FROM observations o JOIN worlds w ON w.world_id=o.world_id "
                    "WHERE o.obs_id=?", (sid,)).fetchone()
            elif sid.startswith("exp_"):
                row = cx.execute(
                    "SELECT e.world_id AS world_id, e.exp_id AS exp_id, "
                    "NULL AS obs_id, w.client_id AS client_id, "
                    "w.seed_root AS seed_root, w.topology_group AS tg "
                    "FROM experiments e JOIN worlds w ON w.world_id=e.world_id "
                    "WHERE e.exp_id=?", (sid,)).fetchone()
            elif sid.startswith("wld_"):
                row = cx.execute(
                    "SELECT world_id, NULL AS exp_id, NULL AS obs_id, "
                    "client_id, seed_root, topology_group AS tg "
                    "FROM worlds WHERE world_id=?", (sid,)).fetchone()
            if row is None or row["client_id"] != client_id:
                unresolved += 1
                continue
            key = {"observation": row["obs_id"], "experiment": row["exp_id"],
                   "world": row["world_id"], "seed_root": row["seed_root"],
                   "topology_group": row["tg"]}[unit]
            if key is None:
                unresolved += 1
                continue
            units.add(key)
        return {"verified_n": len(units), "sources_submitted": len(source_set),
                "sources_unresolved": unresolved}

    def analysis_report(self, world_id: str, exp_id: str, *,
                        client_id: Optional[str] = None) -> dict:
        """The SEALED verification, read back from the ledger rather than
        recomputed. The engine stores the source set's HASH, not the set, so
        there is nothing to recompute from -- and that is the honest design: the
        verification is a fact recorded at registration inside the world's hash
        chain, not a number regenerated later from state that may have moved."""
        cx = self.store.read()
        self._authorize(cx, world_id, client_id)
        ex = cx.execute("SELECT * FROM experiments WHERE exp_id=? AND "
                        "world_id=?", (exp_id, world_id)).fetchone()
        if ex is None:
            raise NotFound("experiment not in this world", exp_id=exp_id)
        if ex["source_set_hash"] is None:
            raise NotFound(
                "this experiment is not an analysis: it declares no source set",
                exp_id=exp_id)
        ev = cx.execute(
            "SELECT payload FROM events WHERE world_id=? AND "
            "event_type='ANALYSIS_REGISTERED' AND refs LIKE ? "
            "ORDER BY world_index DESC LIMIT 1",
            (world_id, '%"' + exp_id + '"%')).fetchone()
        sealed = json.loads(ev["payload"]) if ev is not None else {}
        return {"exp_id": exp_id, "world_id": world_id,
                "unit_of_analysis": ex["unit_of_analysis"],
                "declared_n": ex["declared_n"],
                "source_set_hash": ex["source_set_hash"],
                "spec_hash": ex["spec_hash"],
                "committed_seq": ex["committed_seq"],
                "sealed_verification": sealed}

    # ---- work attestation --------------------------------------------------

    def work_attestation(self, work_id: str, *,
                         client_id: Optional[str] = None) -> dict:
        """What the EXECUTOR said it ran, beside what the engine SEALED.

        The engine holds the requested configuration already -- spec_hash, frozen
        at commit and order-proved by committed_seq. What it never had was the
        executed side, so a run that quietly used a different config produced a
        result indistinguishable from a faithful one. Three hashes and a
        comparison close that; the engine understands none of the parameters."""
        cx = self.store.read()
        r = cx.execute("SELECT * FROM work_items WHERE work_id=?",
                       (work_id,)).fetchone()
        if r is None:
            raise NotFound("unknown work item", work_id=work_id)
        if client_id is not None:
            self._authorize(cx, r["world_id"], client_id)
        ex = cx.execute("SELECT exp_id, spec_hash FROM experiments WHERE "
                        "work_id=?", (work_id,)).fetchone()
        att = {f: r[f] for f in ATTESTATION_FIELDS}
        out = {"work_id": work_id, "world_id": r["world_id"],
               "status": r["status"], "result_hash": r["result_hash"],
               "exp_id": None if ex is None else ex["exp_id"],
               "requested_config_hash": None if ex is None else ex["spec_hash"],
               "attestation": att,
               "attested": any(v is not None for v in att.values())}
        if ex is not None and att["executed_config_hash"] is not None:
            out["config_match"] = (att["executed_config_hash"] == ex["spec_hash"])
        else:
            out["config_match"] = None
        return out

    # ================= v7 measurement identity and meaning ===============
    #
    # observations.content is freeform BY DESIGN, so nothing ever said which
    # field of it was the outcome. That single gap is behind the engine's
    # loudest decline -- "computing a variance requires knowing which field is
    # the outcome, and that is interpretation" -- and behind an analyst reading
    # a plausible column instead of the right one.
    #
    # A DECLARED path does not make the engine a statistician. It makes
    # LOCATING the value a lookup instead of a guess. The engine still computes
    # nothing over it.

    def register_measurement(self, name: str, version: str, *,
                             implementation_hash: str, domain: str,
                             params: Optional[dict] = None,
                             inputs: Optional[list] = None,
                             outputs: Optional[list] = None,
                             provenance: Optional[dict] = None,
                             validation_status: str = "UNVALIDATED",
                             value_path: Optional[str] = None,
                             direction: Optional[str] = None,
                             unit: Optional[str] = None,
                             range_min: Optional[float] = None,
                             range_max: Optional[float] = None,
                             client_id: Optional[str] = None) -> dict:
        """Register a measurement DEFINITION: what it is, where its value
        lives, and what a value means.

        `(name, version)` is UNIQUE and a definition is never silently
        replaced -- a changed oracle needs a new version, because two runs
        scored by different definitions under one name are not comparable and
        nothing downstream could tell.

        v7 adds the half that was missing: `value_path` says WHERE in an
        observation's content this measurement's value is (a dotted path), and
        `direction` / `unit` / `range_min` / `range_max` say what a value
        MEANS. Without direction, "0.2 vs 0.4" is not even orderable, and an
        automated analyst that guesses the sign produces a confident answer
        with the wrong one."""
        if direction is not None and direction not in MEASUREMENT_DIRECTIONS:
            raise ValidationError("unknown direction", direction=direction,
                                  allowed=sorted(MEASUREMENT_DIRECTIONS))
        if value_path is not None:
            _check_value_path(value_path)
        if (range_min is not None and range_max is not None
                and range_min > range_max):
            raise ValidationError("range_min exceeds range_max",
                                  range_min=range_min, range_max=range_max)
        ident = measurement_identity(name, version, implementation_hash,
                                     params or {}, value_path)
        mid = new_id("measurement")
        with self.store.write() as cx:
            try:
                cx.execute(
                    "INSERT INTO measurements(measurement_id,name,version,"
                    "implementation_hash,params,domain,inputs,outputs,"
                    "provenance,validation_status,value_path,direction,unit,"
                    "range_min,range_max,identity_hash,created_ts) "
                    "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (mid, name, version, implementation_hash,
                     json.dumps(params or {}), domain, json.dumps(inputs or []),
                     json.dumps(outputs or []), json.dumps(provenance or {}),
                     validation_status, value_path, direction, unit,
                     range_min, range_max, ident, now()))
            except Exception as e:                                 # noqa: BLE001
                if "UNIQUE" in str(e):
                    raise ValidationError(
                        "measurement (name,version) already registered; a new "
                        "definition needs a new version -- oracles are not "
                        "silently replaced", name=name, version=version)
                raise
            events.append_foundry(
                cx, "MEASUREMENT_REGISTERED", actor=client_id or "foundry",
                scope_kind="measurement", scope_id=mid,
                payload={"name": name, "version": version,
                         "implementation_hash": implementation_hash,
                         "value_path": value_path, "direction": direction,
                         "identity_hash": ident,
                         "engine_source_hash": release.ENGINE_SOURCE_HASH})
        return self.get_measurement(mid)

    def get_measurement(self, measurement_id: str) -> dict:
        r = self.store.read().execute(
            "SELECT * FROM measurements WHERE measurement_id=? OR "
            "identity_hash=?", (measurement_id, measurement_id)).fetchone()
        if r is None:
            raise NotFound("unknown measurement",
                           measurement_id=measurement_id)
        return _measurement_dict(r)

    def list_measurements(self, *, name: Optional[str] = None,
                          domain: Optional[str] = None,
                          limit: int = 100) -> list:
        q, args = "SELECT * FROM measurements WHERE 1=1", []
        if name is not None:
            q += " AND name=?"
            args.append(name)
        if domain is not None:
            q += " AND domain=?"
            args.append(domain)
        q += " ORDER BY name, version LIMIT ?"
        args.append(int(limit))
        return [_measurement_dict(r)
                for r in self.store.read().execute(q, args).fetchall()]

    def read_measured_value(self, world_id: str, obs_id: str,
                            measurement_id: str, *,
                            client_id: Optional[str] = None) -> dict:
        """Resolve ONE observation's value for ONE registered measurement.

        This is a LOOKUP, not an analysis: the engine walks the declared path
        and reports what is there, plus whether it is inside the declared
        range. It computes nothing across observations and takes no view on
        what the number means."""
        cx = self.store.read()
        self._authorize(cx, world_id, client_id)
        o = cx.execute("SELECT * FROM observations WHERE obs_id=? AND "
                       "world_id=?", (obs_id, world_id)).fetchone()
        if o is None:
            raise NotFound("observation not in this world", obs_id=obs_id)
        m = self.get_measurement(measurement_id)
        if not m["value_path"]:
            raise ValidationError(
                "this measurement declares no value_path, so the engine has "
                "no way to say which field of a freeform observation is its "
                "value", measurement_id=measurement_id)
        found, value = _dig(json.loads(o["content"]), m["value_path"])
        out = {"obs_id": obs_id, "world_id": world_id,
               "measurement_id": m["measurement_id"],
               "identity_hash": m["identity_hash"],
               "value_path": m["value_path"], "found": found, "value": value,
               "direction": m["direction"], "unit": m["unit"],
               "evidence_class": o["evidence_class"]}
        if found and isinstance(value, (int, float)) \
                and not isinstance(value, bool):
            lo, hi = m["range_min"], m["range_max"]
            out["in_declared_range"] = (
                (lo is None or value >= lo) and (hi is None or value <= hi))
        return out

    # ================= v7 cross-seat read contract =======================
    #
    # Every read route is owner-scoped, which is right (I5) and which made an
    # ARCHAEOLOGIST impossible: a seat that mines another seat's executed
    # record could see nothing at all, and its only recourse was to open the
    # SQLite file off disk -- no tenancy filter, no evidence-class filter, no
    # schema guard, no contract.
    #
    # A grant is scoped to a TOPOLOGY GROUP because that id is already a
    # server-issued unguessable capability two clients can only come to share
    # deliberately (H5). It is READ ONLY, revocable, and it never widens the
    # owner-scoped routes: the cross-seat surface is separate and says so, so
    # an ordinary read can never quietly start returning someone else's rows.

    def create_read_scope(self, client_id: str, *, name: str,
                          note: Optional[str] = None) -> dict:
        """A curated set of YOUR OWN worlds, existing only to be granted for
        reading. Separate from topology_group on purpose: that field gates
        _may_cross, so granting read over a group would confer artifact-import
        eligibility as a side effect, and the corpus that actually needs
        granting is worlds that already exist and must not be mutated."""
        if not isinstance(name, str) or not name.strip():
            raise ValidationError("a read scope needs a name")
        sid = new_id("scope")
        with self.store.write() as cx:
            if cx.execute("SELECT 1 FROM clients WHERE client_id=?",
                          (client_id,)).fetchone() is None:
                raise NotFound("unknown client", client_id=client_id)
            cx.execute("INSERT INTO read_scopes(scope_id,owner_client_id,name,"
                       "note,created_ts) VALUES(?,?,?,?,?)",
                       (sid, client_id, name, note, now()))
            events.append_foundry(cx, "READ_SCOPE_CREATED", actor=client_id,
                                  scope_kind="read_scope", scope_id=sid,
                                  payload={"name": name, "note": note})
        return self.get_read_scope(sid, client_id=client_id)

    def add_scope_worlds(self, scope_id: str, world_ids: list, *,
                         client_id: str) -> dict:
        """Add worlds you OWN to a scope you OWN. Nothing about the world
        changes -- no field is written on it -- so adding it here cannot alter
        what may cross between worlds."""
        added, skipped = [], []
        with self.store.write() as cx:
            sc = cx.execute("SELECT * FROM read_scopes WHERE scope_id=?",
                            (scope_id,)).fetchone()
            if sc is None or sc["owner_client_id"] != client_id:
                raise NotFound("unknown read scope", scope_id=scope_id)
            for wid in world_ids:
                w = cx.execute("SELECT client_id FROM worlds WHERE world_id=?",
                               (wid,)).fetchone()
                if w is None or w["client_id"] != client_id:
                    skipped.append(wid)       # not yours: silently not added
                    continue
                cx.execute("INSERT OR IGNORE INTO read_scope_worlds(scope_id,"
                           "world_id,added_ts) VALUES(?,?,?)",
                           (scope_id, wid, now()))
                added.append(wid)
            events.append_foundry(cx, "READ_SCOPE_WORLDS_ADDED",
                                  actor=client_id, scope_kind="read_scope",
                                  scope_id=scope_id,
                                  payload={"added": len(added),
                                           "skipped": len(skipped)})
        return {"scope_id": scope_id, "added": added, "not_yours": skipped,
                "total": self.get_read_scope(scope_id,
                                             client_id=client_id)["worlds"]}

    def get_read_scope(self, scope_id: str, *, client_id: str) -> dict:
        cx = self.store.read()
        sc = cx.execute("SELECT * FROM read_scopes WHERE scope_id=?",
                        (scope_id,)).fetchone()
        if sc is None or sc["owner_client_id"] != client_id:
            raise NotFound("unknown read scope", scope_id=scope_id)
        n = cx.execute("SELECT COUNT(*) n FROM read_scope_worlds WHERE "
                       "scope_id=?", (scope_id,)).fetchone()["n"]
        return {"scope_id": scope_id, "owner_client_id": sc["owner_client_id"],
                "name": sc["name"], "note": sc["note"], "worlds": n,
                "created_ts": sc["created_ts"]}

    def list_read_scopes(self, client_id: str) -> list:
        cx = self.store.read()
        return [self.get_read_scope(r["scope_id"], client_id=client_id)
                for r in cx.execute(
                    "SELECT scope_id FROM read_scopes WHERE owner_client_id=? "
                    "ORDER BY created_ts", (client_id,)).fetchall()]

    def grant_read(self, scope_id: str, *, grantee_client_id: str,
                   granted_by: str, note: Optional[str] = None) -> dict:
        """Grant READ over one scope. Only the scope's owner may grant, so a
        capability cannot be re-lent by whoever it reaches."""
        with self.store.write() as cx:
            g = cx.execute("SELECT * FROM read_scopes WHERE scope_id=?",
                           (scope_id,)).fetchone()
            if g is None or g["owner_client_id"] != granted_by:
                # NOT FOUND rather than FORBIDDEN: a group id is a capability,
                # and distinguishing "exists but not yours" would make this an
                # existence oracle for other clients' groups.
                raise NotFound("unknown read scope", scope_id=scope_id)
            if cx.execute("SELECT 1 FROM clients WHERE client_id=?",
                          (grantee_client_id,)).fetchone() is None:
                raise NotFound("unknown grantee", client_id=grantee_client_id)
            if grantee_client_id == granted_by:
                raise ValidationError(
                    "a client already reads its own worlds; a grant to "
                    "yourself would only obscure who can see what")
            prior = cx.execute(
                "SELECT * FROM read_grants WHERE scope_id=? AND "
                "grantee_client_id=?", (scope_id, grantee_client_id)).fetchone()
            if prior is not None and prior["revoked_ts"] is None:
                return _grant_dict(prior)
            gid = new_id("grant")
            if prior is not None:                      # re-grant after revoke
                cx.execute("DELETE FROM read_grants WHERE grant_id=?",
                           (prior["grant_id"],))
            cx.execute(
                "INSERT INTO read_grants(grant_id,scope_id,grantee_client_id,"
                "granted_by,note,created_ts) VALUES(?,?,?,?,?,?)",
                (gid, scope_id, grantee_client_id, granted_by, note, now()))
            events.append_foundry(
                cx, "READ_GRANTED", actor=granted_by, scope_kind="read_scope",
                scope_id=scope_id,
                payload={"grant_id": gid, "grantee": grantee_client_id,
                         "note": note, "regrant": prior is not None})
            return _grant_dict(cx.execute(
                "SELECT * FROM read_grants WHERE grant_id=?",
                (gid,)).fetchone())

    def revoke_read(self, grant_id: str, *, client_id: str) -> dict:
        """Revoke. The row is kept with revoked_ts set: a grant that existed
        and was withdrawn is a different fact from one that never existed, and
        an audit of who could see what WHEN needs both."""
        with self.store.write() as cx:
            r = cx.execute("SELECT * FROM read_grants WHERE grant_id=?",
                           (grant_id,)).fetchone()
            if r is None or r["granted_by"] != client_id:
                raise NotFound("unknown grant", grant_id=grant_id)
            if r["revoked_ts"] is not None:
                return _grant_dict(r)
            cx.execute("UPDATE read_grants SET revoked_ts=? WHERE grant_id=?",
                       (now(), grant_id))
            events.append_foundry(
                cx, "READ_REVOKED", actor=client_id, scope_kind="read_scope",
                scope_id=r["scope_id"],
                payload={"grant_id": grant_id,
                         "grantee": r["grantee_client_id"]})
            return _grant_dict(cx.execute(
                "SELECT * FROM read_grants WHERE grant_id=?",
                (grant_id,)).fetchone())

    def list_read_grants(self, client_id: str) -> dict:
        cx = self.store.read()
        out = {"granted_by_me": [], "granted_to_me": []}
        for r in cx.execute("SELECT * FROM read_grants WHERE granted_by=? "
                            "ORDER BY created_ts", (client_id,)).fetchall():
            out["granted_by_me"].append(_grant_dict(r))
        for r in cx.execute("SELECT * FROM read_grants WHERE "
                            "grantee_client_id=? AND revoked_ts IS NULL "
                            "ORDER BY created_ts", (client_id,)).fetchall():
            out["granted_to_me"].append(_grant_dict(r))
        return out

    def _granted_scopes(self, cx, client_id: str) -> list:
        return [r["scope_id"] for r in cx.execute(
            "SELECT scope_id FROM read_grants WHERE grantee_client_id=? AND "
            "revoked_ts IS NULL", (client_id,)).fetchall()]

    def read_worlds(self, client_id: str, *, group_id: Optional[str] = None,
                    limit: int = 500) -> dict:
        """The cross-seat read surface for WORLDS.

        Returns only worlds the caller does NOT own, in groups it has been
        granted. Own worlds are deliberately excluded: mixing them would let a
        caller lose track of which rows are its own evidence and which are
        another seat's, and that distinction is the whole point of recording
        the corpus tenancy."""
        cx = self.store.read()
        scopes = self._granted_scopes(cx, client_id)
        if group_id is not None:
            # an ungranted scope yields EMPTY, never 403 -- no existence oracle
            scopes = [g for g in scopes if g == group_id]
        if not scopes:
            return {"worlds": [], "scopes": [], "corpus_tenancy": []}
        qs = ",".join("?" * len(scopes))
        rows = cx.execute(
            "SELECT w.* FROM worlds w JOIN read_scope_worlds rw "
            "ON rw.world_id = w.world_id WHERE rw.scope_id IN (%s) AND "
            "w.client_id != ? ORDER BY w.created_ts DESC LIMIT ?" % qs,
            (*scopes, client_id, int(limit))).fetchall()
        tenancy = {}
        for r in rows:
            tenancy[r["client_id"]] = tenancy.get(r["client_id"], 0) + 1
        return {"worlds": [_world_dict(r) for r in rows],
                "scopes": scopes,
                "corpus_tenancy": [{"client_id": k, "worlds": v}
                                   for k, v in sorted(tenancy.items())]}

    def read_observations(self, client_id: str, *,
                          group_id: Optional[str] = None,
                          world_id: Optional[str] = None,
                          evidence_class: Optional[str] = None,
                          limit: int = 1000) -> dict:
        """The cross-seat read surface for OBSERVATIONS.

        `corpus` is returned beside the rows on purpose. An archaeologist's
        first scientific obligation is to say what population it drew from,
        and the commonest way to fail is to pool tenancies and evidence classes
        without noticing. The engine cannot stop a bad analysis, but it can
        refuse to hand over rows without also handing over their provenance."""
        if evidence_class is not None and evidence_class not in EVIDENCE_CLASSES:
            raise ValidationError("unknown evidence_class",
                                  evidence_class=evidence_class,
                                  allowed=list(EVIDENCE_CLASSES))
        cx = self.store.read()
        scopes = self._granted_scopes(cx, client_id)
        if group_id is not None:
            scopes = [g for g in scopes if g == group_id]
        if not scopes:
            return {"observations": [], "corpus": {"worlds": 0, "by_client": [],
                                                   "by_evidence_class": []}}
        qs = ",".join("?" * len(scopes))
        q = ("SELECT o.*, w.client_id AS owner FROM observations o "
             "JOIN worlds w ON w.world_id=o.world_id "
             "JOIN read_scope_worlds rw ON rw.world_id = w.world_id "
             "WHERE rw.scope_id IN (%s) AND w.client_id != ?" % qs)
        args = [*scopes, client_id]
        if world_id is not None:
            q += " AND o.world_id=?"
            args.append(world_id)
        if evidence_class is not None:
            q += " AND o.evidence_class=?"
            args.append(evidence_class)
        q += " ORDER BY o.created_seq LIMIT ?"
        args.append(int(limit))
        rows = cx.execute(q, args).fetchall()
        by_client, by_ev, worlds = {}, {}, set()
        for r in rows:
            by_client[r["owner"]] = by_client.get(r["owner"], 0) + 1
            by_ev[r["evidence_class"]] = by_ev.get(r["evidence_class"], 0) + 1
            worlds.add(r["world_id"])
        return {
            "observations": [_observation_dict(r) for r in rows],
            "corpus": {
                "worlds": len(worlds),
                "scopes": scopes,
                "by_client": [{"client_id": k, "observations": v}
                              for k, v in sorted(by_client.items())],
                "by_evidence_class": [{"evidence_class": k, "observations": v}
                                      for k, v in sorted(by_ev.items())],
                "filtered_evidence_class": evidence_class,
                "truncated": len(rows) >= int(limit)},
        }

    # ================= measurements ====================================
    # ================= observability + accounting ======================
    def verify_world(self, world_id: str, *,
                     client_id: Optional[str] = None) -> dict:
        """Recompute + verify the world's hash chain. Ownership is enforced
        like every other world-scoped read: client_id=None is an INTERNAL call
        from an already-authorized path (world_status); any external caller
        must pass a client_id and owns the world or is denied (closes the
        latent authorization gap flagged in review -- a future route wired to
        this method fails closed by construction)."""
        cx = self.store.read()
        if client_id is not None:
            self._authorize(cx, world_id, client_id)
        return events.verify_world(cx, world_id)

    def world_events(self, world_id: str, *, client_id: Optional[str] = None,
                     limit: int = 100) -> list:
        cx = self.store.read()
        self._authorize(cx, world_id, client_id)
        rows = cx.execute("SELECT * FROM events WHERE world_id=? ORDER BY "
                          "world_index DESC LIMIT ?", (world_id, limit)).fetchall()
        return [events._row_to_event(r) for r in rows][::-1]

    def world_history(self, world_id: str, *,
                      client_id: Optional[str] = None) -> list:
        cx = self.store.read()
        self._authorize(cx, world_id, client_id)
        return events.world_history(cx, world_id)

    def epistemic_accounting(self, world_id: str, *,
                             client_id: Optional[str] = None) -> dict:
        """Mechanically-derived world statistics (section 19). Every number is a
        COUNT over authoritative rows/events -- no narration."""
        cx = self.store.read()
        self._authorize(cx, world_id, client_id)

        def one(sql, *a):
            return cx.execute(sql, (world_id, *a)).fetchone()[0]
        hyp = one("SELECT COUNT(*) FROM hypotheses WHERE world_id=?")
        preds = one("SELECT COUNT(*) FROM predictions WHERE world_id=?")
        exps = one("SELECT COUNT(*) FROM experiments WHERE world_id=?")
        committed = one("SELECT COUNT(*) FROM experiments WHERE world_id=? "
                        "AND committed_seq IS NOT NULL")
        obs = one("SELECT COUNT(*) FROM observations WHERE world_id=?")
        obs_prosp = one("SELECT COUNT(*) FROM observations WHERE world_id=? "
                        "AND pred_prospective=1")
        obs_retro = one("SELECT COUNT(*) FROM observations WHERE world_id=? "
                        "AND pred_id IS NOT NULL AND pred_prospective=0")
        obs_engine = one("SELECT COUNT(*) FROM observations WHERE world_id=? "
                         "AND evidence_class='ENGINE_WORK_RESULT'")
        obs_asserted = one("SELECT COUNT(*) FROM observations WHERE world_id=? "
                           "AND evidence_class='CLIENT_ASSERTED'")
        fals = one("SELECT COUNT(*) FROM hypotheses WHERE world_id=? AND "
                   "state='FALSIFIED'")
        surv = one("SELECT COUNT(*) FROM hypotheses WHERE world_id=? AND "
                   "state='SURVIVED'")
        fails = one("SELECT COUNT(*) FROM failures WHERE world_id=?")
        # a failure is CONSUMED if it is the src of a CONSUMED_BY edge
        consumed = one(
            "SELECT COUNT(DISTINCT src_id) FROM lineage_edges WHERE world_id=? "
            "AND relation='CONSUMED_BY' AND src_kind='failure'")
        muts_from_fail = one(
            "SELECT COUNT(*) FROM lineage_edges WHERE world_id=? AND "
            "relation='CONSUMED_BY' AND src_kind='failure' AND "
            "dst_kind IN ('hypothesis','experiment')")
        return {
            "hypotheses_proposed": hyp, "predictions_registered": preds,
            "experiments_created": exps, "experiments_committed": committed,
            "observations_recorded": obs,
            "observations_prospectively_predicted": obs_prosp,
            "observations_with_retrospective_binding": obs_retro,
            "observations_engine_attested": obs_engine,
            "observations_client_asserted": obs_asserted,
            "claims_falsified": fals, "claims_surviving": surv,
            "failures_generated": fails, "failures_consumed": consumed,
            "failure_consumption_rate": (consumed / fails) if fails else 0.0,
            "mutations_attributed_to_failure": muts_from_fail,
            "unused_failure_count": fails - consumed,
            # NB: these three distinctions are section-8 load-bearing --
            # claimed consumption != causal lineage != empirical usefulness.
            "note": ("failures_consumed counts CLAIMED references only; whether "
                     "a consumed failure improved search is a separate "
                     "empirical question, not implied by this count"),
        }

    def world_status(self, world_id: str, *,
                     client_id: Optional[str] = None) -> dict:
        cx = self.store.read()
        r = self._authorize(cx, world_id, client_id)
        t = now()
        qd = {row["status"]: row["n"] for row in cx.execute(
            "SELECT status, COUNT(*) n FROM work_items WHERE world_id=? "
            "GROUP BY status", (world_id,)).fetchall()}
        active_workers = [x["claimed_by"] for x in cx.execute(
            "SELECT DISTINCT claimed_by FROM work_items WHERE world_id=? AND "
            "status IN ('CLAIMED','RUNNING') AND lease_expires>? AND "
            "claimed_by IS NOT NULL", (world_id, t)).fetchall()]
        expired = cx.execute(
            "SELECT COUNT(*) n FROM work_items WHERE world_id=? AND status IN "
            "('CLAIMED','RUNNING') AND lease_expires<=?",
            (world_id, t)).fetchone()["n"]
        fail_by_type = {x["failure_type"]: x["n"] for x in cx.execute(
            "SELECT failure_type, COUNT(*) n FROM failures WHERE world_id=? "
            "GROUP BY failure_type", (world_id,)).fetchall()}
        ckp = cx.execute("SELECT COUNT(*) n, MAX(world_index) m FROM "
                         "checkpoints WHERE world_id=?", (world_id,)).fetchone()
        try:
            integrity = self.verify_world(world_id)
            integrity_ok = integrity["ok"]
        except Exception as e:                       # noqa: BLE001
            integrity_ok = False
        return {
            "world_id": world_id, "state": r["state"],
            "queue_depth": qd,
            "active_workers": active_workers,
            "active_worker_count": len(active_workers),
            "expired_leases": expired,
            "resources": self.budget_status(world_id),
            "failure_counts": fail_by_type,
            "event_count": r["next_index"],
            "checkpoints": {"count": ckp["n"], "latest_index": ckp["m"]},
            "epistemics": self.epistemic_accounting(world_id),
            "ledger_integrity_ok": integrity_ok,
            "head_hash": r["head_hash"],
            "engine": release.identity(),      # exact running build (DFX-3)
        }

    # ================= lineage / failure queries ========================
    def descendants(self, world_id: str, kind: str, obj_id: str, *,
                    relations: Optional[set] = None) -> list:
        """All research objects reachable FROM (kind,obj_id) by recorded edges
        (section 10). BFS over lineage_edges within the world; the DAG is the
        recorded references, never reconstructed."""
        cx = self.store.read()
        seen, frontier, out = {(kind, obj_id)}, [(kind, obj_id)], []
        while frontier:
            nk, nid = frontier.pop()
            q = ("SELECT dst_kind,dst_id,relation FROM lineage_edges WHERE "
                 "world_id=? AND src_kind=? AND src_id=?")
            for e in cx.execute(q, (world_id, nk, nid)).fetchall():
                if relations and e["relation"] not in relations:
                    continue
                node = (e["dst_kind"], e["dst_id"])
                out.append({"kind": e["dst_kind"], "id": e["dst_id"],
                            "relation": e["relation"], "via": (nk, nid)})
                if node not in seen:
                    seen.add(node); frontier.append(node)
        return out

    def ancestors(self, world_id: str, kind: str, obj_id: str) -> list:
        cx = self.store.read()
        seen, frontier, out = {(kind, obj_id)}, [(kind, obj_id)], []
        while frontier:
            nk, nid = frontier.pop()
            for e in cx.execute("SELECT src_kind,src_id,relation FROM "
                                "lineage_edges WHERE world_id=? AND dst_kind=? "
                                "AND dst_id=?", (world_id, nk, nid)).fetchall():
                node = (e["src_kind"], e["src_id"])
                out.append({"kind": e["src_kind"], "id": e["src_id"],
                            "relation": e["relation"], "of": (nk, nid)})
                if node not in seen:
                    seen.add(node); frontier.append(node)
        return out

    def query_failures(self, world_id: str, *, failure_type: Optional[str] = None,
                       consumed: Optional[bool] = None,
                       client_id: Optional[str] = None) -> list:
        cx = self.store.read()
        self._authorize(cx, world_id, client_id)
        q, a = "SELECT * FROM failures WHERE world_id=?", [world_id]
        if failure_type:
            q += " AND failure_type=?"; a.append(failure_type)
        rows = [dict(r) for r in cx.execute(q, tuple(a)).fetchall()]
        if consumed is not None:
            cons = {e["src_id"] for e in cx.execute(
                "SELECT DISTINCT src_id FROM lineage_edges WHERE world_id=? AND "
                "relation='CONSUMED_BY' AND src_kind='failure'",
                (world_id,)).fetchall()}
            rows = [r for r in rows
                    if (r["failure_id"] in cons) == consumed]
        return rows


def _artifact_dict(r) -> dict:
    return {"artifact_id": r["artifact_id"], "world_id": r["world_id"],
            "kind": r["kind"], "blob_hash": r["blob_hash"],
            "meta": json.loads(r["meta"]), "origin": r["origin"],
            "source_world": r["source_world"],
            "source_artifact": r["source_artifact"]}


def _world_dict(r) -> dict:
    return {"world_id": r["world_id"], "session_id": r["session_id"],
            "client_id": r["client_id"], "name": r["name"], "state": r["state"],
            "parent_world_id": r["parent_world_id"], "fork_point": r["fork_point"],
            "sharing_policy": r["sharing_policy"],
            "topology_group": r["topology_group"], "seed_root": r["seed_root"],
            "created_ts": r["created_ts"], "terminated_ts": r["terminated_ts"],
            "next_index": r["next_index"], "head_hash": r["head_hash"],
            "require_attestation": bool(r["require_attestation"])}


def _experiment_dict(r) -> dict:
    return {"exp_id": r["exp_id"], "world_id": r["world_id"],
            "hyp_id": r["hyp_id"], "pred_id": r["pred_id"],
            "spec": json.loads(r["spec"]), "spec_hash": r["spec_hash"],
            "work_id": r["work_id"], "state": r["state"],
            "committed_seq": r["committed_seq"],
            "committed_ts": r["committed_ts"],
            "unit_of_analysis": r["unit_of_analysis"],
            "declared_n": r["declared_n"],
            "source_set_hash": r["source_set_hash"],
            "is_analysis": r["source_set_hash"] is not None,
            "created_ts": r["created_ts"], "created_seq": r["created_seq"]}


def _observation_dict(r) -> dict:
    return {"obs_id": r["obs_id"], "world_id": r["world_id"],
            "exp_id": r["exp_id"], "pred_id": r["pred_id"],
            "content": json.loads(r["content"]), "outcome": r["outcome"],
            "pred_prospective": r["pred_prospective"],
            "evidence_class": r["evidence_class"],
            "evidence_role": r["evidence_role"], "work_id": r["work_id"],
            "created_ts": r["created_ts"], "created_seq": r["created_seq"]}


def _work_dict(r) -> dict:
    return {"work_id": r["work_id"], "world_id": r["world_id"], "kind": r["kind"],
            "payload": json.loads(r["payload"]), "status": r["status"],
            "priority": r["priority"], "attempts": r["attempts"],
            "max_attempts": r["max_attempts"], "claimed_by": r["claimed_by"],
            "claim_id": r["claim_id"],
            "lease_expires": r["lease_expires"], "heartbeat_ts": r["heartbeat_ts"],
            "result": json.loads(r["result"]) if r["result"] else None,
            "result_hash": r["result_hash"], "error": r["error"],
            "dedup_key": r["dedup_key"],
            "attestation": {f: r[f] for f in ATTESTATION_FIELDS}}


def _claim_dict(r) -> dict:
    return {"claim_id": r["claim_id"], "client_id": r["client_id"],
            "family_id": r["family_id"],
            "analysis_exp_id": r["analysis_exp_id"],
            "analysis_world_id": r["analysis_world_id"],
            "estimand": r["estimand"], "status": r["status"],
            "relevance_floor": json.loads(r["relevance_floor"])
                               if r["relevance_floor"] else None,
            "replication": json.loads(r["replication"])
                           if r["replication"] else {},
            "transport_domain": json.loads(r["transport_domain"])
                                if r["transport_domain"] else None,
            "content_hash": r["content_hash"], "created_ts": r["created_ts"]}
