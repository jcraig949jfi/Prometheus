"""G14 cryptographic sealing: anchor + beacon providers, rule-fixed round
selection, deterministic derivation. FAIL CLOSED everywhere.

PRODUCTION SEMANTICS (identical for mock and real providers; only the
`mock` flag differs, and the scientific admission path structurally refuses
mock attestations):

  1. registration artifact exists and is hash-committed (the ledger event);
  2. the commit hash is anchored EXTERNALLY -> attested anchor_time;
  3. the eligible beacon round is FIXED BY RULE:
       round_id = first round with round_time STRICTLY > anchor_time
     -- no nearest-pulse, no designation, no retry-until-favorable;
  4. the beacon value of that round (and no other) seeds the derivation;
  5. seeds, reference draws, role permutations, and tie-breaks are pure
     functions of (commit_hash, beacon_value, purpose, index) -- nothing
     else: no clock, no environment, no filesystem, no network;
  6. anyone can re-derive bit-exactly from the ledger record alone.

If the anchor or beacon is unavailable: raise. There is no fallback to
local randomness, no alternate provider selected after seeing a round, and
no "temporary" procedural mode. An unavailable seal means no evidence.

PRODUCTION PROVIDERS ARE NOT CHOSEN HERE. Real deployments need external
operational decisions (which public beacon, which timestamping authority,
credentials, SLAs). This module fixes the INTERFACE and semantics; the
review packet recommends concrete candidates (e.g. drand for randomness,
RFC3161 TSA or a public chain for anchoring) and leaves selection to the
adjudication seat. The mock providers exist for offline qualification and
stamp mock=True into every attestation they produce.
"""
from __future__ import annotations

import hashlib


class SealError(Exception):
    pass


class AnchorProvider:
    """Interface: attest that `payload_hash` existed at an externally
    verifiable time. Returns {anchor_time:int, anchor_id:str, mock:bool}."""

    name = "abstract"

    def anchor(self, payload_hash: str) -> dict:
        raise NotImplementedError


class BeaconProvider:
    """Interface: a public randomness beacon with fixed genesis and period.
    round_at(t) is the RULE -- pure arithmetic, no discretion."""

    name = "abstract"
    genesis = 0
    period = 10

    def first_round_after(self, anchor_time: int) -> int:
        """First round whose pulse time is STRICTLY after anchor_time."""
        k = (anchor_time - self.genesis) // self.period + 1
        return max(1, k)

    def round_time(self, round_id: int) -> int:
        return self.genesis + round_id * self.period

    def value(self, round_id: int) -> str:
        raise NotImplementedError


class MockAnchor(AnchorProvider):
    """Offline qualification anchor: a monotone counter held OUTSIDE the
    attacker's reach in the threat model. mock=True always."""

    name = "mock-anchor"

    def __init__(self):
        self._t = 100

    def anchor(self, payload_hash: str) -> dict:
        self._t += 7
        return {"anchor_time": self._t,
                "anchor_id": f"mock-{self._t}-{payload_hash[:8]}",
                "provider": self.name, "mock": True}


class MockBeacon(BeaconProvider):
    """Offline qualification beacon. The pulse value derives from a hidden
    server seed the attacker does not hold; in hostile harnesses the seed
    is generated AFTER the attacker commits, which is the property the real
    beacon provides by physics/operations. mock=True always. A round's
    value is undefined (raises) before its pulse time -- there is no
    peeking at future rounds even in the mock."""

    name = "mock-beacon"
    genesis = 0
    period = 10

    def __init__(self, server_seed: str, now_fn):
        self._seed = server_seed
        self._now = now_fn

    def value(self, round_id: int) -> str:
        if self.round_time(round_id) > self._now():
            raise SealError(f"beacon round {round_id} has not occurred yet "
                            f"-- FAIL CLOSED, no early pulses")
        return hashlib.sha256(
            f"{self._seed}|{round_id}".encode()).hexdigest()


def derive(commit_hash: str, beacon_value: str, purpose: str, index) -> int:
    """THE derivation: pure function of (commit, beacon, purpose, index).
    64-bit integer for seeding downstream deterministic machinery."""
    h = hashlib.sha256(
        f"{commit_hash}|{beacon_value}|{purpose}|{index}".encode()).digest()
    return int.from_bytes(h[:8], "big")


def role_permutation(commit_hash: str, beacon_value: str, block: int,
                     n_slots: int) -> list:
    """Beacon-uniform permutation of slots (Fisher-Yates, derived stream)."""
    perm = list(range(n_slots))
    x = derive(commit_hash, beacon_value, "roles", block)
    for i in range(n_slots - 1, 0, -1):
        x = (x * 6364136223846793005 + 1442695040888963407) % (1 << 64)
        j = x % (i + 1)
        perm[i], perm[j] = perm[j], perm[i]
    return perm


def tie_break(commit_hash: str, beacon_value: str, block: int, slot: int) -> int:
    return derive(commit_hash, beacon_value, f"tie-{block}", slot)


def seal_candidate(store, cand_id: str, commit_hash: str,
                   anchor: AnchorProvider, beacon: BeaconProvider,
                   lt: int) -> dict:
    """Run the full seal sequence against the ledger. Returns the beacon
    attestation. Raises on any unavailability -- fail closed."""
    att = anchor.anchor(commit_hash)
    store.append({"type": "ANCHOR_ATTEST", "lt": lt, "cand_id": cand_id,
                  "payload_hash": commit_hash,
                  "anchor_time": att["anchor_time"],
                  "anchor_id": att["anchor_id"],
                  "provider": att["provider"], "mock": att["mock"]})
    rid = beacon.first_round_after(att["anchor_time"])
    val = beacon.value(rid)                    # raises if round not yet pulsed
    store.append({"type": "BEACON_ATTEST", "lt": lt + 1, "cand_id": cand_id,
                  "round_id": rid, "round_id_expected": rid,
                  "round_time": beacon.round_time(rid), "value_hex": val,
                  "provider": beacon.name,
                  "mock": isinstance(beacon, MockBeacon)})
    return {"round_id": rid, "value_hex": val}
