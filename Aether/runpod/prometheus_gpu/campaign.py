"""Scout -> calibrate -> campaign as ONE path, with re-scout on refusal.

Iteration 2 flew the scout path as three commands. Between them, capacity
for the scouted card vanished twice (FAILURE_PLAYBOOK 22), and the
recovery -- a fresh UNPINNED scout, a new calibration on whatever card it
got, the campaign pinned to that card -- was done by hand. This module is
that recovery, written once, so the better path is also the easy one.

The steps are injected callables, so the whole chain is qualified against
fakes and a seat can drive it with its own flight function:

  fly_scout()                   -> scout receipt (unpinned: walks the
                                   declared alternatives)
  calibrate(scout_receipt)      -> campaign plan dict from
                                   `scout.plan_campaign` (PROCEED/REFUSE)
  fly_campaign(plan, gpu)       -> campaign receipt, pinned to `gpu`

WHAT IT WILL NOT DO. It never retries a campaign that ran, or one whose
create was ambiguous: only a campaign the provider CONFIRMED created
nothing for capacity (`disposition.cause == "NO_CAPACITY"`) earns a
re-scout. It never reshapes a REFUSEd plan. It stops after
`max_rescouts`, and says why.
"""

from . import receipt as rc

# Re-scouting spends money on a new scout each time; one is what
# Iteration 2's manual recovery needed.
DEFAULT_MAX_RESCOUTS = 1


def _cause(receipt_obj):
    return ((receipt_obj or {}).get("disposition") or {}).get("cause")


def _actual(receipt_obj):
    return ((receipt_obj or {}).get("cost") or {}).get("usd_estimated")


def run(fly_scout, calibrate, fly_campaign, max_rescouts=DEFAULT_MAX_RESCOUTS,
        log=lambda m: None):
    """Returns a summary dict. Every flight's receipt is in `flights`."""
    flights = []
    summary = {"schema": "prometheus-gpu/auto-campaign/1", "flights": flights,
               "decision": None, "stopped_because": None, "estimates": None,
               "rescouts": 0}
    scouts_left = 1 + int(max_rescouts)
    while scouts_left > 0:
        scouts_left -= 1
        scout = fly_scout()
        flights.append({"role": "scout", "receipt": scout})
        if scout is None or scout.get("result") != "OK":
            summary["stopped_because"] = (
                "scout did not complete (%s); nothing was calibrated and no "
                "campaign was attempted"
                % (_cause(scout) or (scout or {}).get("result")))
            return summary
        gpu = scout.get("gpu_used")
        plan = calibrate(scout)
        summary["decision"] = plan.get("decision")
        summary["plan"] = plan
        if plan.get("decision") != "PROCEED":
            summary["stopped_because"] = (
                "the calibrated plan REFUSED the campaign; the proposal is in "
                "`plan` and adopting it is the seat's decision")
            return summary
        log("campaign pinned to %s (the card the scout measured)" % gpu)
        camp = fly_campaign(plan, gpu)
        flights.append({"role": "campaign", "receipt": camp, "gpu": gpu})
        if camp is not None and _cause(camp) == "NO_CAPACITY" and scouts_left:
            summary["rescouts"] += 1
            log("no capacity for %s; re-scouting unpinned" % gpu)
            continue
        pre = (plan.get("preregistered_estimate") or {}).get("expected_usd")
        cal = (plan.get("calibrated_estimate") or {}).get("expected_usd")
        summary["estimates"] = rc.estimates_block(pre, cal, _actual(camp))
        summary["campaign_result"] = (camp or {}).get("result")
        if camp is not None and _cause(camp) == "NO_CAPACITY":
            summary["stopped_because"] = (
                "no capacity for the calibrated card after %d re-scout(s)"
                % summary["rescouts"])
        return summary
    summary["stopped_because"] = "re-scout budget exhausted"
    return summary
