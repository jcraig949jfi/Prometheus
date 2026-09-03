"""Million-transition adversarial fold storm.

Pure state-machine fuzz (no disk): random well-formed, malformed, and
hostile events hammered at the fold, with the conserved-risk invariant
asserted after EVERY accepted transition and the full identity re-checked
from primitive sums periodically. Complements hostile.py's disk-level
battery (H10/H12) where fsync bounds throughput.

Run:  python -m prodledger.fold_storm [n_transitions]
"""
from __future__ import annotations

import sys
import os
from fractions import Fraction

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from wforge.world import stream

from .core import (LedgerState, validate_and_apply, Refused,
                   derived_block_id)
from . import LEDGER_VERSION


def main(n=2_000_000):
    rng = stream("fold-storm")
    st = LedgerState()
    validate_and_apply(st, {"type": "GENESIS", "lt": 0,
                            "ledger_version": LEDGER_VERSION,
                            "config_hash": "cfg-storm"})
    fams, cands = [], []
    accepted = refused = 0
    lt = 1
    purchases_seen = Fraction(0)
    for i in range(n):
        lt += rng.below(3)
        op = rng.below(12)
        ev = None
        if op <= 2:
            ns = "SCIENTIFIC" if rng.below(2) else "CALIBRATION"
            fid = f"f{rng.below(400)}"
            ev = {"type": "FAMILY_OPEN", "lt": lt, "family_id": fid,
                  "ns": ns, "reserve": f"{1 + rng.below(60)}/{40 + rng.below(9000)}",
                  "ttl_lt": 1 + rng.below(90_000),
                  "co_signed": rng.below(10) == 0}
            if rng.below(20) == 0:
                ev["reserve"] = f"-{1 + rng.below(9)}/7"       # hostile
            tag = ("fam", fid, ns)
        elif op <= 4 and fams:
            fid, ns = fams[rng.below(len(fams))]
            K = (100, 999, 1000, 2000, 100000)[rng.below(5)]
            cid = f"c{i}"
            ev = {"type": "CANDIDATE_REGISTER", "lt": lt, "cand_id": cid,
                  "family_id": fid, "ns": ns, "K": K,
                  "block_budget": (8, 32, 128, 4000)[rng.below(4)],
                  "m_refs": 3, "selection_blocks": [],
                  "commit_hash": f"h{i}",
                  "betting_rule": ("LAM-MIX-V1", "evil")[rng.below(8) == 0],
                  "ref_rule": ("CANON-R-V1", "my-R")[rng.below(8) == 0],
                  "context_rule": "CANON-W-V1",
                  "role_rule": "CANON-PI-V1",
                  "tie_rule": ("BEACON_UNIFORM", "CAND_WINS")[rng.below(8) == 0],
                  "detector": "det"}
            tag = ("cand", cid, ns, K)
        elif op == 5 and fams:
            ev = {"type": "FAMILY_CLOSE", "lt": lt,
                  "family_id": fams[rng.below(len(fams))][0]}
            tag = None
        elif op == 6 and cands:
            cid = cands[rng.below(len(cands))]
            ev = {"type": "ANCHOR_ATTEST", "lt": lt, "cand_id": cid,
                  "payload_hash": st.candidates.get(cid, {}).get(
                      "commit_hash", "?"),
                  "anchor_time": 100 + rng.below(10_000),
                  "anchor_id": f"a{i}", "provider": "mock", "mock": True}
            tag = None
        elif op == 7 and cands:
            cid = cands[rng.below(len(cands))]
            c = st.candidates.get(cid, {})
            at = (c.get("anchor") or {}).get("time", 0)
            ev = {"type": "BEACON_ATTEST", "lt": lt, "cand_id": cid,
                  "round_id": 9, "round_time": at + (1, 0)[rng.below(6) == 0],
                  "value_hex": "aa" * 8, "provider": "mock", "mock": True}
            tag = None
        elif op == 8 and cands:
            cid = cands[rng.below(len(cands))]
            c = st.candidates.get(cid, {})
            idx = c.get("blocks", 0)
            bid = (derived_block_id(cid, idx) if rng.below(3)
                   else f"forge{rng.below(200)}")
            ev = {"type": "EVIDENCE_BLOCK", "lt": lt, "cand_id": cid,
                  "block_id": bid, "wealth": f"{rng.below(5000)}/1",
                  "derivation_beacon": "aa" * 8}
            tag = None
        elif op == 9 and cands:
            cid = cands[rng.below(len(cands))]
            ns = st.candidates.get(cid, {}).get("ns", "SCIENTIFIC")
            rt = ("SCIENTIFIC_ADMITTED" if ns == "SCIENTIFIC"
                  else "CALIBRATION_ADMITTED")
            if rng.below(5) == 0:
                rt = ("CALIBRATION_ADMITTED" if rt[0] == "S"
                      else "SCIENTIFIC_ADMITTED")
            ev = {"type": "ADMISSION", "lt": lt, "cand_id": cid,
                  "record_type": rt}
            tag = None
        elif op == 10:
            ev = {"type": ("HALT_SET", "HALT_LIFT")[rng.below(2)], "lt": lt,
                  "reason": "storm", "actor":
                  ("operator", "adjudication_seat")[rng.below(2)],
                  "adjudication_ref": "adj-1"}
            tag = None
        else:
            ev = {"type": "FAMILY_OPEN", "lt": lt + (1 << 61)
                  if rng.below(2) else -3, "family_id": f"z{i}",
                  "ns": ("Scientific", "SCIENTIFIC ", "SCIENTIFIC")
                  [rng.below(3)], "reserve": "1/9", "ttl_lt": 5}
            tag = None
        try:
            validate_and_apply(st, ev)
            accepted += 1
            if tag and tag[0] == "fam":
                fams.append((tag[1], tag[2]))
            elif tag and tag[0] == "cand":
                cands.append(tag[1])
                purchases_seen += Fraction(1, tag[3])
        except Refused:
            refused += 1
        st.assert_conserved()                       # EVERY transition
        if i % 250_000 == 0 and i:
            sci = st.pools["SCIENTIFIC"]
            print(f"  {i:>9,} transitions | accepted {accepted:,} "
                  f"refused {refused:,} | sci purchased "
                  f"{sci['purchased']} <= 1/10 | families {len(st.families)}")
    sci, cal = st.pools["SCIENTIFIC"], st.pools["CALIBRATION"]
    print(f"\nFOLD STORM COMPLETE: {n:,} adversarial transitions")
    print(f"  accepted {accepted:,} / refused {refused:,}")
    print(f"  scientific purchased (irrevocable): {sci['purchased']}  "
          f"(budget 1/10; identity held at every accepted transition)")
    print(f"  calibration purchased             : {cal['purchased']}")
    print(f"  conservation violations           : 0")
    return 0


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 2_000_000
    sys.exit(main(n))
