"""Hierarchical admission-rights ledger -- gates G9a + G9b.

DERIVED FROM THE PREREGISTERED GUARANTEE, per adjudication (never chosen by
intuition):

  GUARANTEE. Under the complete Observatory null, the EXPECTED NUMBER of
  false ADMITTED_MICROSTRUCTURE records over the lifetime of the instrument
  is at most ALPHA_LIFE.  (Proposed ALPHA_LIFE = 0.1; number adjudicable.)

CONSTRUCTION (admission-rights ledger):
  * The global ledger opens with wealth ALPHA_LIFE, in admission-risk units.
  * G9a -- a FAMILY, at instantiation, RESERVES w_f <= remaining global
    wealth. The family PROCESS is priced at creation, whatever its origin
    (human, miner, LLM). Unbounded family generation is impossible: wealth
    is finite and debited up front.
  * G9b -- a CANDIDATE admission test, at REGISTRATION, PURCHASES a
    threshold K_c at price 1/K_c, debited from its family's reservation.
    No candidate holds an independent alpha entitlement because its family
    paid an entrance fee: every test is individually priced.
  * ADMISSION iff the candidate's anytime-valid wealth process E_c ever
    reaches K_c on its admission evidence.

WHY THE GUARANTEE HOLDS (and exactly when):
    E[#false admissions] = sum_c P(E_c >= K_c | H0_c)
                         <= sum_c 1/K_c            (Ville, per candidate)
                         <= ALPHA_LIFE             (ledger conservation)
  The bound uses only linearity of expectation, so it survives ARBITRARY
  dependence between candidates (shared worlds, shared founders, correlated
  evidence), unbounded candidate and family counts, and adaptive
  data-driven family generation -- PROVIDED two preconditions, which this
  ledger ENFORCES rather than assumes:

  PRECONDITION 1 (REGISTRATION-BEFORE-EVIDENCE). K_c is fixed at
    registration, BEFORE any admission-stage evidence is unsealed. The
    ledger refuses to accept evidence for an unregistered candidate and
    refuses to change K_c after registration. Violation is catastrophic,
    not marginal: peek at n null candidates, purchase only for observed
    crossers at K = E_observed, and realized false admissions exceed ledger
    spend by ~K-fold (demonstrated numerically in ledger_demo).

  PRECONDITION 2 (EVIDENCE DISJOINTNESS). Admission evidence blocks are
    disjoint from the evidence that SELECTED the candidate (the two-stage
    discipline). The ledger records the selection-evidence block ids at
    registration and rejects admission evidence that intersects them.

  NO RECREDITING in V1: wealth is never returned, even for admissions that
  later replicate. (An alpha-investing extension with an FDR-type guarantee
  is a V2 design question; it requires theory this file does not claim.)

WHAT THE NUMBERS MEAN IN PRACTICE (stated so nobody is surprised later):
  ALPHA_LIFE = 0.1 with admissions at K = 200 (price 0.005) funds at most
  20 admission ATTEMPTS over the instrument's lifetime. Attempts are
  precious BY DESIGN: preservation and flagging are free annotation,
  investigation is rationed compute, and admission tests are rare, priced
  events. A program whose deliverable is ONE particle should feel this.
"""
from __future__ import annotations

from fractions import Fraction


class LedgerError(Exception):
    pass


# Preregistered mechanical bounds (red-team L4/L5; values adjudicable):
K_MIN = 100                    # price cap 1/100: no single purchase can eat
                               # more than 1% of a 1.0 budget or 10% of 0.1
RESERVE_CAP = Fraction(1, 4)   # a family may reserve <= 25% of remaining
                               # global wealth unless adjudicator-co-signed
PER_BLOCK_MAX_MULT = Fraction(13, 4)   # max wealth multiplier per block under
                               # the LAM_GRID mixture with m=3 refs (payoff 4)


class AdmissionLedger:
    """Append-only in spirit: every action emits an immutable entry.
    Production backs this with the SFE hash-chained ledger; the prototype
    keeps the entries list and enforces the same refusals.

    WHAT THE PROTOTYPE ENFORCES vs RECORDS (stated so nobody confuses them):
      ENFORCED here: reservation caps, K bounds and reachability, purchase
        pricing, one-time-use evidence blocks, selection/admission
        disjointness, registration-before-evidence ordering, K immutability.
      RECORDED here, ENFORCED by the production seal protocol: CRYPTOGRAPHIC
        sealing. In a deterministic substrate a procedural ordering is
        unenforceable -- an adversary can precompute every E_c offline
        before registering (red-team FATAL). Production therefore derives
        admission-block seeds, reference assignments, and candidate/
        reference ROLE PERMUTATIONS from PUBLIC BEACON randomness occurring
        AFTER the registration commit; admission is invalid unless seed
        provenance verifies against the post-commit beacon. The prototype
        carries the attestation fields and refuses evidence lacking them."""

    def __init__(self, alpha_life: Fraction):
        self.alpha_life = Fraction(alpha_life)
        self.global_remaining = Fraction(alpha_life)
        self.families = {}        # family_id -> {"reserved":F, "remaining":F, "open":bool}
        self.candidates = {}      # cand_id -> record
        self.used_blocks = set()  # ONE-TIME-USE: a block serves ONE candidate ever
        self.entries = []

    def _log(self, kind, **kw):
        self.entries.append({"seq": len(self.entries), "kind": kind, **kw})

    # ---- G9a ----------------------------------------------------------
    def open_family(self, family_id: str, reserve: Fraction, origin: str,
                    ttl_entries: int = 100_000, co_signed: bool = False):
        reserve = Fraction(reserve)
        if family_id in self.families:
            raise LedgerError("family exists")
        if reserve <= 0 or reserve > self.global_remaining:
            raise LedgerError(
                f"reservation {reserve} exceeds remaining global wealth "
                f"{self.global_remaining} -- the family process is priced; "
                f"unbounded family generation is structurally impossible")
        if not co_signed and reserve > self.global_remaining * RESERVE_CAP:
            raise LedgerError(
                f"reservation {reserve} exceeds {RESERVE_CAP} of remaining "
                f"wealth -- land-grab refused; larger reservations require "
                f"adjudicator co-signature")
        self.global_remaining -= reserve
        self.families[family_id] = {
            "reserved": reserve, "remaining": reserve, "open": True,
            "origin": origin, "expires_at": len(self.entries) + ttl_entries,
        }
        self._log("FAMILY_OPENED", family=family_id, reserve=str(reserve),
                  origin=origin, co_signed=co_signed,
                  global_remaining=str(self.global_remaining))

    def close_family(self, family_id: str):
        """Unspent reservation returns to the global pool. Safe: returned
        wealth was never at risk (no candidate purchased against it)."""
        f = self.families[family_id]
        if not f["open"]:
            raise LedgerError("already closed")
        f["open"] = False
        self.global_remaining += f["remaining"]
        self._log("FAMILY_CLOSED", family=family_id,
                  returned=str(f["remaining"]))
        f["remaining"] = Fraction(0)

    # ---- G9b ----------------------------------------------------------
    def register_candidate(self, cand_id: str, family_id: str, K: int,
                           selection_block_ids: frozenset,
                           block_budget: int, m_refs: int = 3):
        """K, the block budget, and the reference count m are ALL fixed now,
        jointly, before any admission evidence exists (red-team: an
        m-references knob adjusted after unsealing is a rank-rigging dial).
        selection_block_ids are recorded for the disjointness refusal."""
        if cand_id in self.candidates:
            raise LedgerError("candidate exists; K is immutable")
        f = self.families.get(family_id)
        if f is None or not f["open"]:
            raise LedgerError("no open family")
        if len(self.entries) > f["expires_at"]:
            raise LedgerError("family reservation expired (TTL); unspent "
                              "wealth returns to the pool")
        if K < K_MIN:
            raise LedgerError(
                f"K={K} below preregistered floor {K_MIN} -- a single cheap-"
                f"threshold purchase must not be able to drain the lifetime "
                f"budget")
        if Fraction(K) > PER_BLOCK_MAX_MULT ** block_budget:
            raise LedgerError(
                f"K={K} unreachable within block budget {block_budget} "
                f"(max wealth {float(PER_BLOCK_MAX_MULT)}^{block_budget}) -- "
                f"an unwinnable test is not a test")
        price = Fraction(1, K)
        if price > f["reserved"] / 2:
            raise LedgerError(
                f"price 1/{K} exceeds half the family's original reservation "
                f"{f['reserved']} -- single-purchase cap")
        if price > f["remaining"]:
            raise LedgerError(
                f"price 1/{K} exceeds family remaining {f['remaining']} -- "
                f"no candidate holds an alpha entitlement its family cannot fund")
        f["remaining"] -= price
        self.candidates[cand_id] = {
            "family": family_id, "K": K, "price": price,
            "block_budget": block_budget, "m_refs": m_refs,
            "selection_blocks": frozenset(selection_block_ids),
            "evidence_blocks": set(), "wealth_peak": Fraction(1),
            "registered_seq": len(self.entries),
            "state": "REGISTERED",
        }
        self._log("CANDIDATE_REGISTERED", cand=cand_id, family=family_id,
                  K=K, price=str(price), block_budget=block_budget,
                  m_refs=m_refs)

    def submit_evidence(self, cand_id: str, block_id: str,
                        wealth_after: Fraction,
                        beacon_round_seq: int = -1):
        """Refusals enforced here: selection/admission disjointness;
        ONE-TIME-USE blocks (a block ever used by ANY candidate is
        permanently contaminated for every other -- the cross-candidate
        evidence-reuse laundering channel is closed structurally); block
        budget; and the beacon attestation (the block's seed derivation
        must reference a public-randomness round that POSTDATES this
        candidate's registration -- verified cryptographically in
        production, carried as a refused-if-absent attestation here)."""
        c = self.candidates.get(cand_id)
        if c is None:
            raise LedgerError(
                "evidence for unregistered candidate REFUSED -- "
                "registration-before-evidence is the load-bearing rule")
        if c["state"] not in ("REGISTERED", "TESTING"):
            raise LedgerError(f"candidate is {c['state']}")
        if beacon_round_seq <= c["registered_seq"]:
            raise LedgerError(
                "evidence block lacks a post-registration beacon attestation "
                "REFUSED -- in a deterministic substrate, procedural ordering "
                "is not sealing; evidence must be underivable at registration")
        if block_id in c["selection_blocks"]:
            raise LedgerError(
                "admission evidence intersects selection evidence REFUSED -- "
                "the two-stage discipline is not optional")
        if block_id in self.used_blocks:
            raise LedgerError(
                "block already consumed by a registration REFUSED -- "
                "one-time-use blocks close the cross-candidate reuse channel")
        if len(c["evidence_blocks"]) >= c["block_budget"]:
            raise LedgerError("registered block budget exhausted")
        self.used_blocks.add(block_id)
        c["evidence_blocks"].add(block_id)
        c["state"] = "TESTING"
        w = Fraction(wealth_after)
        if w > c["wealth_peak"]:
            c["wealth_peak"] = w
        if c["wealth_peak"] >= c["K"]:
            c["state"] = "ADMITTED"
            self._log("ADMITTED", cand=cand_id, K=c["K"],
                      peak=str(c["wealth_peak"]))
        return c["state"]

    def spend_summary(self):
        spent = sum((c["price"] for c in self.candidates.values()),
                    Fraction(0))
        bound = sum((Fraction(1, c["K"]) for c in self.candidates.values()),
                    Fraction(0))
        return {
            "alpha_life": self.alpha_life,
            "global_remaining": self.global_remaining,
            "total_candidate_spend": spent,
            "false_admission_expectation_bound": bound,
        }
