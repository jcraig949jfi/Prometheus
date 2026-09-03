"""The conserved-risk state machine. State = pure fold of the event log.

Design rules a maintainer must not "improve" away:
  * NO wall-clock anywhere in a state transition -- logical time (lt) is a
    caller-supplied monotone integer validated on append; TTLs are in lt, so
    replay is deterministic forever.
  * NO separate debit step -- the accepted PURCHASE event IS the debit; a
    crash either persisted the event (state includes it) or did not (state
    excludes it, and the caller never got an acknowledgement).
  * Purchases are irrevocable. There is no code path that reduces
    `purchased`. Reservation release touches only never-purchased wealth.
  * Namespace firewall is structural: separate pools, separate floors,
    separate admission record types, and a scientific admission validates
    the full anchor+beacon chain with mock refusal.
  * Every command either APPENDS exactly one event or raises Refused; a
    Refused command is also logged (REFUSAL event, zero financial effect)
    so audits see attempts, but refusal logging failure never blocks the
    refusal itself.
"""
from __future__ import annotations

import hashlib
from fractions import Fraction

from . import (ALPHA_LIFE_NUM, ALPHA_LIFE_DEN, CALIB_BUDGET_NUM,
               CALIB_BUDGET_DEN, K_MIN_SCIENTIFIC, K_MIN_CALIBRATION,
               LEDGER_VERSION)

PER_BLOCK_MAX_MULT = Fraction(13, 4)
RESERVE_CAP = Fraction(1, 4)
NAMESPACES = ("SCIENTIFIC", "CALIBRATION")

# ---- v1.1 repairs (each constant closes a preserved v1.0 exploit) ----
MAX_LT_STEP = 100_000        # H3: a caller cannot detonate every TTL with one
                             # forged logical-time bomb; lt advances boundedly
BLOCK_BUDGET_CAP = 128       # DoS guard: K_MIN=1000 needs only ~6 winning
                             # blocks at max multiplier; 128 is generous
# H5: rule commitments are PROTOCOL-ENUMERATED, never free-form strings.
# A hash of arbitrary code is not a commitment to fairness (red team):
#  - the reference sampler is canonical (uniform PRF-index into the frozen
#    operator ensemble) -- a registrant-supplied R could tilt the reference
#    law while staying bit-reproducible;
#  - tie handling has exactly two safe values;
#  - betting rules come from the fairness-certified family (mixture betting
#    with sum_r payout(r)/(m+1) <= 1, machine-checked at enumeration time).
CANON_REF_RULE = "CANON-R-V1"
CANON_ROLE_RULE = "CANON-PI-V1"
CANON_CONTEXT_RULES = ("CANON-W-V1",)
TIE_RULES = ("BEACON_UNIFORM", "STRICT_TOP_ONLY")
BETTING_RULES = ("LAM-MIX-V1",)


def derived_block_id(cand_id: str, index: int) -> str:
    """H6: block ids are DERIVED, never caller-named -- structural
    uniqueness that no other candidate can consume."""
    return "blk-" + hashlib.sha256(
        f"{cand_id}|{index}".encode("ascii")).hexdigest()[:24]


class Refused(Exception):
    """A command the ledger will not accept. Deliberately loud."""


def frac(s) -> Fraction:
    if isinstance(s, Fraction):
        return s
    if isinstance(s, str) and "/" in s:
        n, d = s.split("/")
        return Fraction(int(n), int(d))
    if isinstance(s, int):
        return Fraction(s)
    raise Refused(f"exact rational required, got {s!r} (floats are refused)")


def sfrac(f: Fraction) -> str:
    return f"{f.numerator}/{f.denominator}"


class LedgerState:
    """Folded state. Never mutated except through apply()."""

    def __init__(self):
        self.genesis = None
        self.lt = -1
        self.pools = {}          # ns -> {"budget","unreserved","purchased"}
        self.families = {}       # fid -> dict
        self.candidates = {}     # cid -> dict
        self.used_blocks = set() # global one-time-use evidence blocks
        self.halted = False
        self.halt_reason = None
        self.n_events = 0

    # ---------- conservation ----------
    def conservation(self, ns: str) -> tuple:
        p = self.pools[ns]
        reserved = sum((f["remaining"] for f in self.families.values()
                        if f["ns"] == ns and f["open"]), Fraction(0))
        total = p["unreserved"] + reserved + p["purchased"]
        return total, p["budget"]

    def assert_conserved(self):
        for ns in self.pools:
            total, budget = self.conservation(ns)
            if total != budget:
                raise AssertionError(
                    f"CONSERVATION VIOLATED ns={ns}: {total} != {budget}")
            if self.pools[ns]["purchased"] > budget:
                raise AssertionError(f"OVERSPEND ns={ns}")

    # ---------- lazy deterministic TTL ----------
    def _expire(self, lt: int):
        """Deterministic: a family whose TTL has passed at this event's lt
        releases its UNSPENT remainder back to the pool. Runs before every
        command evaluation, so ordering is fixed by the log itself."""
        for fid in sorted(self.families):
            f = self.families[fid]
            if f["open"] and lt > f["expires_lt"]:
                self.pools[f["ns"]]["unreserved"] += f["remaining"]
                f["remaining"] = Fraction(0)
                f["open"] = False
                f["closed_by"] = "TTL"


def validate_and_apply(state: LedgerState, event: dict) -> None:
    """THE state transition. Raises Refused (state unchanged) or mutates.
    Called identically by the live service and by replay: acceptance is a
    property of the event sequence, never of who is running the fold."""
    et = event.get("type")
    lt = event.get("lt")
    if not isinstance(lt, int) or lt < 0:
        raise Refused("lt: nonnegative integer logical time required")

    if state.genesis is None:
        if et != "GENESIS":
            raise Refused("first event must be GENESIS")
        if event.get("ledger_version") != LEDGER_VERSION:
            raise Refused("ledger_version mismatch")
        state.genesis = dict(event)
        state.pools = {
            "SCIENTIFIC": {"budget": Fraction(ALPHA_LIFE_NUM, ALPHA_LIFE_DEN),
                            "unreserved": Fraction(ALPHA_LIFE_NUM, ALPHA_LIFE_DEN),
                            "purchased": Fraction(0)},
            "CALIBRATION": {"budget": Fraction(CALIB_BUDGET_NUM, CALIB_BUDGET_DEN),
                             "unreserved": Fraction(CALIB_BUDGET_NUM, CALIB_BUDGET_DEN),
                             "purchased": Fraction(0)},
        }
        state.lt = lt
        state.n_events += 1
        return

    if et == "GENESIS":
        raise Refused("GENESIS may appear only once")
    if lt < state.lt:
        raise Refused(f"logical time regression: {lt} < {state.lt}")
    if lt > state.lt + MAX_LT_STEP:
        raise Refused(f"logical-time bomb refused: {lt} > watermark "
                      f"{state.lt} + {MAX_LT_STEP} -- TTL detonation via "
                      f"forged clocks is not available")
    state._expire(lt)

    if et == "REFUSAL":
        pass                                           # audit record, no effect

    elif et == "HALT_SET":
        if not event.get("reason"):
            raise Refused("halt requires a reason")
        state.halted = True
        state.halt_reason = event["reason"]

    elif et == "HALT_LIFT":
        if event.get("actor") != "adjudication_seat":
            raise Refused("halt lift requires the adjudication seat -- "
                          "no local operator override exists")
        if not event.get("adjudication_ref"):
            raise Refused("halt lift requires a ledgered adjudication_ref")
        state.halted = False
        state.halt_reason = None

    elif et == "FAMILY_OPEN":
        ns, fid = event.get("ns"), event.get("family_id")
        if ns not in NAMESPACES:
            raise Refused(f"unknown namespace {ns!r}")
        if not fid or fid in state.families:
            raise Refused("family id missing or already exists (ids are "
                          "never reused, including closed/expired ones)")
        reserve = frac(event.get("reserve"))
        ttl = event.get("ttl_lt")
        if not isinstance(ttl, int) or ttl <= 0:
            raise Refused("positive integer ttl_lt required")
        pool = state.pools[ns]
        if reserve <= 0 or reserve > pool["unreserved"]:
            raise Refused(f"reservation {reserve} exceeds unreserved "
                          f"{pool['unreserved']}")
        if not event.get("co_signed"):
            held = sum((f2["remaining"] for f2 in state.families.values()
                        if f2["ns"] == ns and f2["open"]
                        and not f2.get("co_signed")), Fraction(0))
            if held + reserve > pool["budget"] * RESERVE_CAP:
                raise Refused(
                    "AGGREGATE un-co-signed open reservations would exceed "
                    "25% of the namespace budget -- the geometric-grab "
                    "circumvention of a per-open cap is closed")
        pool["unreserved"] -= reserve
        state.families[fid] = {
            "ns": ns, "reserved": reserve, "remaining": reserve,
            "open": True, "expires_lt": lt + ttl, "closed_by": None,
            "co_signed": bool(event.get("co_signed")),
        }

    elif et == "FAMILY_CLOSE":
        f = state.families.get(event.get("family_id"))
        if f is None or not f["open"]:
            raise Refused("no such open family")
        state.pools[f["ns"]]["unreserved"] += f["remaining"]
        f["remaining"] = Fraction(0)
        f["open"] = False
        f["closed_by"] = "CLOSE"

    elif et == "CANDIDATE_REGISTER":
        cid, fid = event.get("cand_id"), event.get("family_id")
        ns = event.get("ns")
        if cid in state.candidates:
            raise Refused("candidate id exists -- registration is immutable; "
                          "K and every committed parameter cannot change")
        f = state.families.get(fid)
        if f is None or not f["open"] or f["ns"] != ns:
            raise Refused("no open family in this namespace")
        if ns == "SCIENTIFIC" and state.halted:
            raise Refused("ADMISSIONS_HALTED_ARTIFACT_CONTROL: no new "
                          "scientific purchases")
        K, B, m = event.get("K"), event.get("block_budget"), event.get("m_refs", 3)
        for v, name in ((K, "K"), (B, "block_budget"), (m, "m_refs")):
            if isinstance(v, bool) or not isinstance(v, int) or v <= 0:
                raise Refused(f"{name}: positive integer required")
        kmin = K_MIN_SCIENTIFIC if ns == "SCIENTIFIC" else K_MIN_CALIBRATION
        if K < kmin:
            raise Refused(f"K={K} below {ns} floor {kmin}")
        if B > BLOCK_BUDGET_CAP:
            raise Refused(f"block_budget {B} above cap {BLOCK_BUDGET_CAP}")
        reach, steps = Fraction(1), 0
        while reach < K and steps < B:
            reach *= PER_BLOCK_MAX_MULT
            steps += 1
        if reach < K:
            raise Refused(f"K={K} unreachable within block budget {B} -- "
                          f"an unwinnable test is not a test")
        price = Fraction(1, K)
        if price > f["reserved"] / 2:
            raise Refused("single purchase exceeds half the family's "
                          "original reservation")
        if price > f["remaining"]:
            raise Refused("family reservation cannot fund this purchase")
        for req in ("commit_hash", "betting_rule", "ref_rule",
                    "context_rule", "role_rule", "tie_rule", "detector"):
            if not event.get(req):
                raise Refused(f"registration missing committed field: {req}")
        if event["ref_rule"] != CANON_REF_RULE:
            raise Refused("reference rule must be the CANONICAL sampler -- "
                          "a registrant-supplied R can tilt the reference "
                          "law while staying bit-reproducible; refused")
        if event["role_rule"] != CANON_ROLE_RULE:
            raise Refused("role permutation is protocol-derived, never "
                          "registrant-supplied")
        if event["context_rule"] not in CANON_CONTEXT_RULES:
            raise Refused("context rule must come from the canonical "
                          "whitelist (W-gerrymandering refused)")
        if event["tie_rule"] not in TIE_RULES:
            raise Refused("tie rule must be BEACON_UNIFORM or "
                          "STRICT_TOP_ONLY -- 'candidate wins ties' is a "
                          "guaranteed-admission machine")
        if event["betting_rule"] not in BETTING_RULES:
            raise Refused("betting rule must come from the fairness-"
                          "certified family -- a hash of arbitrary code is "
                          "not a commitment to fairness")
        f["remaining"] -= price                        # THE irrevocable purchase
        state.pools[ns]["purchased"] += price
        state.candidates[cid] = {
            "ns": ns, "family": fid, "K": K, "price": price,
            "block_budget": B, "m": m,
            "selection_blocks": frozenset(event.get("selection_blocks", [])),
            "commit_hash": event["commit_hash"],
            "registered_lt": lt, "anchor": None, "beacon": None,
            "blocks": 0, "wealth_peak": Fraction(1), "status": "REGISTERED",
        }

    elif et == "ANCHOR_ATTEST":
        c = state.candidates.get(event.get("cand_id"))
        if c is None or c["status"] != "REGISTERED":
            raise Refused("anchor requires a freshly registered candidate")
        if c["anchor"] is not None:
            raise Refused("anchor already attested; immutable")
        if event.get("payload_hash") != c["commit_hash"]:
            raise Refused("anchor payload does not match the registration "
                          "commit -- anchoring something else is not anchoring")
        if not isinstance(event.get("anchor_time"), int):
            raise Refused("integer anchor_time required")
        c["anchor"] = {"time": event["anchor_time"],
                       "provider": event.get("provider", "?"),
                       "mock": bool(event.get("mock", True))}

    elif et == "BEACON_ATTEST":
        c = state.candidates.get(event.get("cand_id"))
        if c is None or c["anchor"] is None:
            raise Refused("beacon attestation requires a prior anchor")
        if c["beacon"] is not None:
            raise Refused("beacon already attested; immutable -- there is "
                          "no round shopping")
        rt = event.get("round_time")
        if not isinstance(rt, int) or rt <= c["anchor"]["time"]:
            raise Refused("beacon round must be STRICTLY after the anchor "
                          "time -- the round is fixed by rule, not chosen")
        expected = event.get("round_id_expected")
        if expected is not None and event.get("round_id") != expected:
            raise Refused("beacon round is not the rule-determined round")
        if not event.get("value_hex"):
            raise Refused("beacon value required")
        c["beacon"] = {"round_id": event.get("round_id"), "round_time": rt,
                       "value_hex": event["value_hex"],
                       "provider": event.get("provider", "?"),
                       "mock": bool(event.get("mock", True))}
        c["status"] = "SEALED"

    elif et == "EVIDENCE_BLOCK":
        c = state.candidates.get(event.get("cand_id"))
        bid = event.get("block_id")
        if c is None:
            raise Refused("evidence for unregistered candidate -- "
                          "registration-before-evidence is the load-bearing rule")
        if c["status"] not in ("SEALED", "TESTING"):
            raise Refused(f"candidate is {c['status']}; evidence refused "
                          f"(no beacon = no evidence: fail closed)")
        if bid != derived_block_id(event.get("cand_id"), c["blocks"]):
            raise Refused("block id must be the DERIVED id "
                          "H(candidate, index) -- caller-named block ids "
                          "allowed cross-candidate burn griefing")
        if bid in state.used_blocks:
            raise Refused("evidence block already consumed -- blocks are "
                          "one-time-use across ALL candidates, forever")
        if bid in c["selection_blocks"]:
            raise Refused("admission evidence intersects selection evidence")
        if c["blocks"] >= c["block_budget"]:
            raise Refused("committed block budget exhausted")
        if event.get("derivation_beacon") != c["beacon"]["value_hex"]:
            raise Refused("block derivation does not cite this candidate's "
                          "beacon value -- provenance unverifiable")
        w = frac(event.get("wealth"))
        if w < 0:
            raise Refused("wealth cannot be negative")
        state.used_blocks.add(bid)
        c["blocks"] += 1
        c["status"] = "TESTING"
        if w > c["wealth_peak"]:
            c["wealth_peak"] = w

    elif et == "ADMISSION":
        c = state.candidates.get(event.get("cand_id"))
        if c is None or c["status"] != "TESTING":
            raise Refused("admission requires a candidate under test")
        if c["wealth_peak"] < c["K"]:
            raise Refused(f"wealth peak {c['wealth_peak']} below K={c['K']} "
                          f"-- no admission without a crossed threshold")
        rec = event.get("record_type")
        if c["ns"] == "SCIENTIFIC":
            if state.halted:
                raise Refused("ADMISSIONS_HALTED_ARTIFACT_CONTROL")
            if rec != "SCIENTIFIC_ADMITTED":
                raise Refused("scientific candidates emit SCIENTIFIC_ADMITTED")
            if c["anchor"]["mock"] or c["beacon"]["mock"]:
                raise Refused("MOCK attestation can NEVER satisfy a "
                              "scientific admission -- structurally refused")
            if c["K"] < K_MIN_SCIENTIFIC:
                raise Refused("scientific K floor violated")
        else:
            if rec != "CALIBRATION_ADMITTED":
                raise Refused("calibration candidates emit CALIBRATION_"
                              "ADMITTED -- there is no upgrade path")
        c["status"] = rec

    else:
        raise Refused(f"unknown event type {et!r}")

    state.lt = lt
    state.n_events += 1
    state.assert_conserved()
