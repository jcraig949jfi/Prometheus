"""WP-X6: the exploration reserve, allocated across FAMILIES first.

Rule R1 (SELECTION_RULES.md): each lane's daily quota is partitioned into an
ESTABLISHED share and a RESERVE share. The reserve may be drawn only by
families that are young or thin. The failure this prevents: an established
family with a hundred templates absorbs every draw a young family with one
template would otherwise get.

Design, per the order:

* **Family first, template second.** A draw chooses an eligible FAMILY by a
  declared bounded-fairness rule (deficit round-robin, deterministic replay),
  then a template within it. A family with 100 templates and a family with 1
  receive the same family-level entitlement (X6-a).
* **Family identity is explicit.** A template names its family in a
  ``family`` field. Templates without one belong to the implicit family
  ``kind:<kind>``, which is ESTABLISHED by construction: an alias or an extra
  template never creates a new entitlement (X6-c).
* **Classification precedence.** established if the family is in the policy's
  ``established`` list; else reserve-eligible if young (admitted within
  ``young_days``) or thin (fewer than ``thin_rows`` published rows in the
  lane); else established. Admission age comes from the family's EARLIEST
  admitted template.
* **Unspent stays unspent.** With no reserve-eligible family the reserve is
  recorded as unspent, never handed to an established family (X6-c).
* **Counters update once per event** (offered, published, failed, withdrawn),
  and a frozen comparison order is never re-derived from later counters or
  timestamps (X6-d): the order is computed from the frozen snapshot only.
* **Inactive until the operator sets the numbers.** No policy file -> the
  producer draws as before and records ``allocation.active = False``. The
  values in ``PROPOSED`` are Archaeon's recommendation, not policy.

Everything here is a pure function of declared inputs so it can be replayed.
"""
from __future__ import annotations

import hashlib
import json
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

POLICY_ID = "allocation.reserve.v0"
POLICY_PATH = Path(__file__).resolve().parent.parent / "policies" / (POLICY_ID + ".json")

#: Archaeon's recommendation (D-6). NOT policy until written to POLICY_PATH by
#: the operator with chosen_by / chosen_on filled in.
PROPOSED: Dict[str, Any] = {
    "policy_id": POLICY_ID,
    "quota_per_day": 6,
    "reserve_draws_per_day": 1,
    "young_days": 90,
    "thin_rows": 24,
    "fairness": "deficit_round_robin",
    "horizon_days": 7,
    "established": ["kind:evaluate_bitstring"],
    "chosen_by": None, "chosen_on": None,
}


def load_policy(path: Optional[Path] = None) -> Dict[str, Any]:
    p = Path(path or POLICY_PATH)
    if not p.exists():
        return dict(PROPOSED, active=False,
                    note="no policy file; values are Archaeon's proposal")
    pol = json.loads(p.read_text(encoding="utf-8"))
    if not pol.get("chosen_by") or not pol.get("chosen_on"):
        return dict(pol, active=False,
                    note="policy file lacks chosen_by/chosen_on; inactive")
    return dict(pol, active=True)


# --------------------------------------------------------------------------
# Family identity and classification
# --------------------------------------------------------------------------
def family_of(template: Dict[str, Any]) -> str:
    fam = template.get("family")
    if fam:
        return str(fam)
    return "kind:{}".format(template["kind"])


def families(templates: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Group admitted templates by family with the earliest admission date."""
    out: Dict[str, Dict[str, Any]] = {}
    for t in templates:
        f = family_of(t)
        rec = out.setdefault(f, {"family": f, "templates": [], "admitted_at": None,
                                 "explicit": bool(t.get("family"))})
        rec["templates"].append(t["template_id"])
        a = t.get("admitted_at")
        if a and (rec["admitted_at"] is None or a < rec["admitted_at"]):
            rec["admitted_at"] = a
    return out


def _age_days(admitted_at: Optional[str], today: date) -> Optional[int]:
    if not admitted_at:
        return None
    try:
        d = datetime.fromisoformat(admitted_at.replace("Z", "+00:00")).date()
    except ValueError:
        d = date.fromisoformat(admitted_at[:10])
    return (today - d).days


def classify(fams: Dict[str, Dict[str, Any]], today: date,
             published_rows: Dict[str, int], policy: Dict[str, Any]
             ) -> Dict[str, Dict[str, Any]]:
    """established | reserve, with the reason. Precedence: policy list,
    implicit kind family, young, thin, else established."""
    out = {}
    for f, rec in fams.items():
        age = _age_days(rec["admitted_at"], today)
        rows = int(published_rows.get(f, 0))
        if f in policy.get("established", []):
            share, why = "established", "listed as established in policy"
        elif not rec["explicit"]:
            share, why = "established", "implicit kind family (no declared family)"
        elif age is not None and age <= int(policy["young_days"]):
            share, why = "reserve", "young: admitted {} days ago".format(age)
        elif rows < int(policy["thin_rows"]):
            share, why = "reserve", "thin: {} rows < {}".format(rows, policy["thin_rows"])
        else:
            share, why = "established", "neither young nor thin"
        out[f] = dict(rec, share=share, reason=why, age_days=age, rows=rows)
    return out


# --------------------------------------------------------------------------
# Deficit round-robin over a frozen snapshot
# --------------------------------------------------------------------------
def _tiebreak(lane: str, day: str, fam: str) -> str:
    return hashlib.sha256("{}|{}|{}|{}".format(POLICY_ID, lane, day, fam)
                          .encode()).hexdigest()


def choose_family(eligible: List[str], served: Dict[str, int],
                  offered_total: int, lane: str, day: str) -> Optional[str]:
    """The eligible family with the largest DEFICIT = fair share so far minus
    times served; ties broken by a seeded hash, never by name order or
    arrival time. Pure: replays from the same inputs."""
    if not eligible:
        return None
    n = len(eligible)
    fair = (offered_total + 1) / n
    scored = sorted(eligible,
                    key=lambda f: (-(fair - served.get(f, 0)), _tiebreak(lane, day, f)))
    return scored[0]


def plan_draw(*, slot_index: int, lane: str, day: str, classified: Dict[str, Dict[str, Any]],
              served: Dict[str, int], offered_total: int, policy: Dict[str, Any]
              ) -> Dict[str, Any]:
    """Decide the SHARE of this slot and the FAMILY it goes to.

    Slot 0..reserve_draws_per_day-1 of the day are reserve slots. A reserve
    slot with no eligible family is recorded UNSPENT and the slot falls back
    to the established share for this draw only -- the unspent count is what
    the census reports, and it is never zeroed by giving it away.
    """
    reserve_slots = int(policy["reserve_draws_per_day"])
    is_reserve_slot = slot_index < reserve_slots
    res_el = sorted(f for f, r in classified.items() if r["share"] == "reserve")
    est_el = sorted(f for f, r in classified.items() if r["share"] == "established")
    out: Dict[str, Any] = {"policy_id": policy.get("policy_id", POLICY_ID),
                           "active": bool(policy.get("active")),
                           "slot_index": slot_index,
                           "slot_share": "reserve" if is_reserve_slot else "established",
                           "reserve_unspent": False}
    if is_reserve_slot and res_el:
        fam = choose_family(res_el, served, offered_total, lane, day)
        out.update(share="reserve", family=fam, eligible_families=res_el)
        return out
    if is_reserve_slot:
        out["reserve_unspent"] = True
        out["reserve_unspent_reason"] = "no reserve-eligible family admitted"
    fam = choose_family(est_el, served, offered_total, lane, day)
    out.update(share="established", family=fam, eligible_families=est_el)
    return out


def count_event(counters: Dict[str, Dict[str, int]], family: str, event: str) -> None:
    """offered | published | failed | withdrawn | quota_exhausted -- once each."""
    if event not in ("offered", "published", "failed", "withdrawn", "quota_exhausted"):
        raise ValueError(event)
    c = counters.setdefault(family, {})
    c[event] = c.get(event, 0) + 1


def freeze_snapshot(classified: Dict[str, Dict[str, Any]], served: Dict[str, int],
                    policy: Dict[str, Any], lane: str, day: str) -> Dict[str, Any]:
    """A frozen allocation snapshot for a comparison campaign. Orders derived
    from it are a function of it alone; later counters cannot change them."""
    body = {"policy": {k: v for k, v in policy.items() if k != "note"},
            "classified": {f: {"share": r["share"], "rows": r["rows"],
                               "age_days": r["age_days"]} for f, r in classified.items()},
            "served": dict(served), "lane": lane, "day": day}
    blob = json.dumps(body, sort_keys=True, separators=(",", ":"), default=str)
    return dict(body, snapshot_hash="sha256:" + hashlib.sha256(blob.encode()).hexdigest())


def order_from_snapshot(snapshot: Dict[str, Any], n_slots: int) -> List[Dict[str, Any]]:
    """The family order for n_slots, from the snapshot only. Deterministic."""
    served = dict(snapshot["served"])
    classified = {f: dict(r) for f, r in snapshot["classified"].items()}
    policy = dict(snapshot["policy"], active=True)
    out = []
    for i in range(n_slots):
        d = plan_draw(slot_index=i % int(policy["quota_per_day"]), lane=snapshot["lane"],
                      day=snapshot["day"], classified=classified, served=served,
                      offered_total=i, policy=policy)
        if d.get("family"):
            served[d["family"]] = served.get(d["family"], 0) + 1
        out.append({"slot": i, "share": d["share"], "family": d.get("family"),
                    "reserve_unspent": d["reserve_unspent"]})
    return out
