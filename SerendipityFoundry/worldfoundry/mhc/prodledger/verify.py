"""Independent conservation verifier.

Reads ONLY the raw immutable log file. Re-implements the accounting from
scratch (deliberately NOT importing core.py's fold -- semantic drift between
service and verifier is itself an attack surface, so the duplication is the
point). Trusts no cached total from any live service.

At EVERY history prefix it asserts the accounting identity, per namespace:

    unreserved + open_reserved_remaining + purchased == BUDGET

and it rejects histories that are tampered (chain breaks, hash mismatches),
impossible (overspend, refund, duplicate purchase identity, block reuse,
time regression), or forged (scientific admission carrying mock
attestations, K below floor, admission without a purchase).

Exact arithmetic only. No float touches money.

Outputs: a human-readable conservation report and a machine-readable dict.
"""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction

ROOT = "0" * 64
ALPHA_LIFE = Fraction(1, 10)
CALIB_BUDGET = Fraction(1000)
K_MIN_SCI, K_MIN_CAL = 1000, 100
MAX_LT_STEP = 100_000
BLOCK_BUDGET_CAP = 128
RESERVE_CAP = Fraction(1, 4)
CANON_RULES = {"ref_rule": "CANON-R-V1", "role_rule": "CANON-PI-V1"}
CONTEXT_RULES = ("CANON-W-V1",)
TIE_RULES = ("BEACON_UNIFORM", "STRICT_TOP_ONLY")
BETTING_RULES = ("LAM-MIX-V1",)


def _derived_block_id(cand_id, index):
    return "blk-" + hashlib.sha256(
        f"{cand_id}|{index}".encode("ascii")).hexdigest()[:24]


class VerifyError(Exception):
    pass


def _canon(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True).encode("ascii")


def _frac(s):
    if isinstance(s, str) and "/" in s:
        n, d = s.split("/")
        return Fraction(int(n), int(d))
    if isinstance(s, int):
        return Fraction(s)
    raise VerifyError(f"non-exact monetary value {s!r}")


def verify(path: str) -> dict:
    pools = {"SCIENTIFIC": {"budget": ALPHA_LIFE, "unreserved": ALPHA_LIFE,
                            "purchased": Fraction(0)},
             "CALIBRATION": {"budget": CALIB_BUDGET, "unreserved": CALIB_BUDGET,
                             "purchased": Fraction(0)}}
    families, candidates, used_blocks = {}, {}, set()
    halted = False
    reservation_history, purchase_history, release_history = [], [], []
    admissions = {"SCIENTIFIC_ADMITTED": 0, "CALIBRATION_ADMITTED": 0}
    prev, lt_prev, n = ROOT, -1, 0
    genesis_seen = False

    def expire(lt):
        for fid in sorted(families):
            f = families[fid]
            if f["open"] and lt > f["expires_lt"]:
                pools[f["ns"]]["unreserved"] += f["remaining"]
                release_history.append((fid, "TTL", f["remaining"]))
                f["remaining"] = Fraction(0)
                f["open"] = False

    def check_identity(where):
        for ns, p in pools.items():
            reserved = sum((f["remaining"] for f in families.values()
                            if f["ns"] == ns and f["open"]), Fraction(0))
            if p["unreserved"] + reserved + p["purchased"] != p["budget"]:
                raise VerifyError(f"IDENTITY BROKEN ns={ns} at {where}")
            if p["purchased"] > p["budget"]:
                raise VerifyError(f"OVERSPEND ns={ns} at {where}")

    with open(path, "rb") as fh:
        for i, line in enumerate(fh):
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line.decode("ascii"))
            if rec["p"] != prev:
                raise VerifyError(f"chain break at record {i}")
            h = hashlib.sha256(prev.encode("ascii") + _canon(rec["e"])).hexdigest()
            if h != rec["h"]:
                raise VerifyError(f"hash mismatch at record {i}")
            prev = h
            e = rec["e"]
            et, lt = e.get("type"), e.get("lt")
            if not isinstance(lt, int) or lt < lt_prev:
                raise VerifyError(f"logical-time violation at record {i}")
            if et != "GENESIS" and et != "REFUSAL"                     and lt > lt_prev + MAX_LT_STEP:
                raise VerifyError(f"logical-time bomb at record {i}")
            lt_prev = max(lt_prev, lt)
            n += 1
            if et == "GENESIS":
                if genesis_seen:
                    raise VerifyError("second GENESIS")
                genesis_seen = True
                continue
            if not genesis_seen:
                raise VerifyError("event before GENESIS")
            expire(lt)
            if et == "FAMILY_OPEN":
                fid, ns = e["family_id"], e["ns"]
                if fid in families:
                    raise VerifyError(f"family id reuse: {fid}")
                r = _frac(e["reserve"])
                if r <= 0 or r > pools[ns]["unreserved"]:
                    raise VerifyError(f"impossible reservation at {i}")
                if not e.get("co_signed"):
                    held = sum((f2["remaining"] for f2 in families.values()
                                if f2["ns"] == ns and f2["open"]
                                and not f2.get("co_signed")), Fraction(0))
                    if held + r > pools[ns]["budget"] * RESERVE_CAP:
                        raise VerifyError(
                            f"aggregate reservation cap violated at {i}")
                pools[ns]["unreserved"] -= r
                families[fid] = {"ns": ns, "reserved": r, "remaining": r,
                                 "open": True, "expires_lt": lt + e["ttl_lt"],
                                 "co_signed": bool(e.get("co_signed"))}
                reservation_history.append((fid, ns, r))
            elif et == "FAMILY_CLOSE":
                f = families.get(e["family_id"])
                if f is None or not f["open"]:
                    raise VerifyError(f"impossible close at {i}")
                pools[f["ns"]]["unreserved"] += f["remaining"]
                release_history.append((e["family_id"], "CLOSE", f["remaining"]))
                f["remaining"] = Fraction(0)
                f["open"] = False
            elif et == "CANDIDATE_REGISTER":
                cid, ns, K = e["cand_id"], e["ns"], e["K"]
                if cid in candidates:
                    raise VerifyError(f"duplicate purchase identity {cid}")
                f = families.get(e["family_id"])
                if f is None or not f["open"] or f["ns"] != ns:
                    raise VerifyError(f"purchase against invalid family at {i}")
                if K < (K_MIN_SCI if ns == "SCIENTIFIC" else K_MIN_CAL):
                    raise VerifyError(f"K floor violated at {i}")
                if e.get("block_budget", 0) > BLOCK_BUDGET_CAP:
                    raise VerifyError(f"block budget cap violated at {i}")
                for fld, want in CANON_RULES.items():
                    if e.get(fld) != want:
                        raise VerifyError(
                            f"non-canonical {fld} at {i} -- validation "
                            f"clause V1/V3 violated")
                if e.get("context_rule") not in CONTEXT_RULES:
                    raise VerifyError(f"non-canonical context rule at {i}")
                if e.get("tie_rule") not in TIE_RULES:
                    raise VerifyError(f"illegal tie rule at {i}")
                if e.get("betting_rule") not in BETTING_RULES:
                    raise VerifyError(f"uncertified betting rule at {i}")
                if ns == "SCIENTIFIC" and halted:
                    raise VerifyError(
                        f"scientific purchase during halt at {i}")
                price = Fraction(1, K)
                if price > f["remaining"] or price > f["reserved"] / 2:
                    raise VerifyError(f"unfundable purchase at {i}")
                f["remaining"] -= price
                pools[ns]["purchased"] += price
                candidates[cid] = {"ns": ns, "K": K, "price": price,
                                   "mock_anchor": None, "mock_beacon": None,
                                   "wealth_peak": Fraction(1), "blocks": 0,
                                   "budget": e["block_budget"]}
                purchase_history.append((cid, ns, K, price))
            elif et == "ANCHOR_ATTEST":
                c = candidates.get(e["cand_id"])
                if c is None or c["mock_anchor"] is not None:
                    raise VerifyError(f"anchor anomaly at {i}")
                c["mock_anchor"] = bool(e.get("mock", True))
                c["anchor_time"] = e["anchor_time"]
            elif et == "BEACON_ATTEST":
                c = candidates.get(e["cand_id"])
                if c is None or c["mock_anchor"] is None \
                        or c["mock_beacon"] is not None:
                    raise VerifyError(f"beacon anomaly at {i}")
                if e["round_time"] <= c["anchor_time"]:
                    raise VerifyError(f"beacon round not after anchor at {i}")
                c["mock_beacon"] = bool(e.get("mock", True))
            elif et == "EVIDENCE_BLOCK":
                c = candidates.get(e["cand_id"])
                bid = e["block_id"]
                if c is None or c["mock_beacon"] is None:
                    raise VerifyError(f"evidence without seal at {i}")
                if bid != _derived_block_id(e["cand_id"], c["blocks"]):
                    raise VerifyError(f"non-derived block id at {i}")
                if bid in used_blocks:
                    raise VerifyError(f"evidence block reuse at {i}")
                if c["blocks"] >= c["budget"]:
                    raise VerifyError(f"block budget exceeded at {i}")
                used_blocks.add(bid)
                c["blocks"] += 1
                w = _frac(e["wealth"])
                if w > c["wealth_peak"]:
                    c["wealth_peak"] = w
            elif et == "ADMISSION":
                c = candidates.get(e["cand_id"])
                if c is None:
                    raise VerifyError(f"admission without purchase at {i}")
                if c["wealth_peak"] < c["K"]:
                    raise VerifyError(f"admission below K at {i}")
                rt = e["record_type"]
                if c["ns"] == "SCIENTIFIC":
                    if halted:
                        raise VerifyError(f"scientific admission during "
                                          f"halt at {i}")
                    if rt != "SCIENTIFIC_ADMITTED":
                        raise VerifyError(f"record-type forgery at {i}")
                    if c["mock_anchor"] or c["mock_beacon"]:
                        raise VerifyError(
                            f"SCIENTIFIC admission with MOCK attestation at {i}")
                    if c["K"] < K_MIN_SCI:
                        raise VerifyError(f"scientific K floor at {i}")
                else:
                    if rt != "CALIBRATION_ADMITTED":
                        raise VerifyError(f"record-type forgery at {i}")
                admissions[rt] += 1
            elif et == "HALT_SET":
                halted = True
            elif et == "HALT_LIFT":
                if e.get("actor") != "adjudication_seat"                         or not e.get("adjudication_ref"):
                    raise VerifyError(f"illegitimate halt lift at {i}")
                halted = False
            elif et == "REFUSAL":
                pass
            else:
                raise VerifyError(f"unknown event type at {i}: {et}")
            check_identity(f"record {i}")

    sci = pools["SCIENTIFIC"]
    report = {
        "records": n,
        "head": prev,
        "alpha_life": str(ALPHA_LIFE),
        "reservations": len(reservation_history),
        "purchases": len(purchase_history),
        "releases": len(release_history),
        "scientific": {
            "unreserved": str(sci["unreserved"]),
            "reserved_unspent": str(sci["budget"] - sci["unreserved"]
                                    - sci["purchased"]),
            "purchased_forever": str(sci["purchased"]),
            "remaining_max_liability": str(sci["budget"] - sci["purchased"]),
        },
        "admissions": admissions,
        "identity_verified_at_every_prefix": True,
    }
    return report


def human_report(rep: dict) -> str:
    s = rep["scientific"]
    return "\n".join([
        "CONSERVATION REPORT (independent refold; exact arithmetic)",
        f"  records verified          : {rep['records']}  head {rep['head'][:16]}...",
        f"  ALPHA_LIFE                : {rep['alpha_life']}",
        f"  scientific unreserved     : {s['unreserved']}",
        f"  scientific reserved(open) : {s['reserved_unspent']}",
        f"  scientific purchased ever : {s['purchased_forever']}   (IRREVOCABLE)",
        f"  max remaining liability   : {s['remaining_max_liability']}",
        f"  admissions                : {rep['admissions']}",
        f"  identity at every prefix  : {rep['identity_verified_at_every_prefix']}",
    ])
