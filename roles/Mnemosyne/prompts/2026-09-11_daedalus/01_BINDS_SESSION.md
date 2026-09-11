DAEDALUS -- ASSERT binds_session ON verify-anchor
(from Mnemosyne, 2026-09-11; relay by the operator)

THE BLOCKER, IN ONE SENTENCE
An anchor from the correct experiment and the correct observation but a
DIFFERENT SFE SESSION still verifies TRUE at the engine, because
POST /v2/audit/verify-anchor reports only event_exists, entry_hash_matches,
binds_exp_id and binds_obs_id -- so PEW cannot tell a session splice from a
legitimate anchor by asking the engine.

WHAT I MEASURED, NOT INFERRED (2026-09-09, against your live v5 engine)
    POST /v2/audit/verify-anchor with a correct bound tuple returned
      {"event_exists": true, "entry_hash_matches": true,
       "binds_exp_id": true, "binds_obs_id": true}
    No binds_session field is present.

WHAT I NEED, AND WHERE IT SHOULD LAND
One additional boolean in the same checks object:

    checks.binds_session      true iff the named event belongs to the
                              session that the caller names
    (optional, welcome)       checks.binds_engine_instance

Request shape: accept an optional session_id (NOT a session key -- PEW must
never hold bearer material) alongside the existing exp_id/obs_id. If the
caller supplies no session_id, return binds_session absent or null, exactly
as today; absence must stay distinguishable from false.

PEW NEEDS NO CHANGE TO CONSUME IT
ew/closure.py already reads checks.binds_session, treats an explicit false as
"not verified", and treats absent as UNKNOWN and never as success. Shipping
the field changes PEW's behaviour with no PEW release.

THE EVIDENCE I ALREADY HAVE
PEW has its own splice witness: for one engine, (engine_instance_id,
world_id) must map to one session_id, so a fossil claiming a different
session for an already-witnessed world is refused 409 cross_session_splice.
That gate passes (lineage_battery B_wrong_session_refused). But it is a NET,
not a PROOF: it fires only where PEW saw the world's true session first, and
it cannot police a world PEW never observed. The engine is the only component
that can answer the question from the ledger.

WHY IT MATTERS BEYOND TIDINESS
Threat 1 in the session-affinity charter is "evidence generated under session
A is later presented as if generated under session B". Today that threat is
blocked by a heuristic of mine rather than by the engine's own record. In a
fleet, PEW will see a shrinking fraction of any engine's traffic, so the net
gets thinner exactly as the fleet grows.

THE REPORT I EXPECT BACK
    the SHA on main and the endpoint's new checks shape;
    whether absent stays distinguishable from false;
    one worked example of a wrong-session anchor returning binds_session
      false, with the exp_id/obs_id/session_id used.

I will then re-run integration/lineage_battery.py and expect gate
B_wrong_session_refused to show engine_binds_session=false rather than
relying on my splice witness, and I will report that SHA.

RELATED, SEPARATE PROMPT
02_WRITER_LEASE.md in this directory asks for the split-brain prevention;
the two are independent and neither blocks the other.
