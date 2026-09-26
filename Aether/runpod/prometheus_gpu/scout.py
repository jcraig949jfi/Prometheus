"""Scout, calibrate, then commit: campaign planning that measures first.

AETH-02 is the motivating regression. Its cost was preregistered at $0.83
per trajectory from a throughput figure carried over from a DIFFERENT
workload -- a larger lattice without the causal-edge observer running.
Measured, it was $0.889. A 7.2% miss, and because the controller ceiling
had been set just above the projection, the third of three trajectories
stopped against the ceiling instead of finishing.

Two lessons, and this module is both of them:

  MEASURE THE WORKLOAD YOU WILL ACTUALLY RUN. A projection is a
  throughput claim wearing a dollar sign. Extrapolating from an
  uninstrumented or materially different workload is guessing, and a
  representative scout costs cents.

  A CEILING IS A GUARDRAIL, NOT A PLAN. Set it above the projection by
  more than the projection's own uncertainty, or a small estimate error
  turns into lost work at the end of the last replicate.

A calibration from a workload that DIFFERS MATERIALLY from the campaign
is not silently usable here. `representativeness` enumerates the
differences, and `plan_campaign` refuses to quote a calibrated estimate
across one unless the caller says in as many words that it accepts them.

THE CONTROLLER NEVER SILENTLY RESHAPES THE SCIENCE. When a campaign does
not fit its ceiling this module returns REFUSE, together with the largest
workload that would fit as a PROPOSAL. Acting on that proposal is the
seat's decision, never the planner's.
"""

import math

from . import cost as cost_mod

# What a scout must share with its campaign for a calibration to carry
# over. Each entry is a thing that, if different, changes seconds per
# unit of work -- which is the only quantity the calibration provides.
MATERIAL = ("gpu_class", "gpu_count", "dependencies", "entrypoint",
            "args", "env", "work_unit_name")

DEFAULT_MARGIN = 0.20          # uncertainty added on top of the estimate
DEFAULT_TEARDOWN_RESERVE_S = 120.0   # retrieval + terminate + confirm


class CampaignRefused(ValueError):
    """The requested campaign does not fit, and reshaping is not ours."""


def _fingerprint(spec):
    gpu = spec["gpu"]
    return {
        "gpu_class": gpu.get("class"),
        "gpu_count": int(gpu.get("count", 1)),
        "dependencies": tuple(sorted(spec["dependencies"].get("pip", []))),
        "entrypoint": spec["entrypoint"],
        "args": tuple(spec["args"]),
        "env": tuple(sorted(spec["env"].items())),
        "work_unit_name": (spec.get("work_units") or {}).get("name"),
    }


def scout_spec(spec, scale, name_suffix="-scout"):
    """A reduced copy of `spec` that is still representative.

    Only the work-unit ESTIMATE and `max_runtime_s` shrink. GPU class,
    dependencies, entrypoint, args and environment are carried over
    unchanged, because those are exactly the things whose difference
    would invalidate the calibration. A scout that quietly dropped the
    instrumentation would reproduce the AETH-02 error precisely.

    The module is expected to read its own work-unit count from its
    environment or args; this sets `work_units.estimate` so the platform
    and the module agree on what the scout is meant to do.
    """
    if not 0 < scale < 1:
        raise ValueError("scale must be in (0, 1); a scout is a fraction of "
                         "the campaign, not a different experiment")
    units = spec.get("work_units")
    if not units:
        raise ValueError("a scout needs work_units: calibration is measured "
                         "in the module's own denominator")
    data = spec.to_dict()
    data["name"] = (spec.name + name_suffix)[:63]
    data["work_units"] = dict(units, estimate=max(1.0,
                                                  units["estimate"] * scale))
    data["max_runtime_s"] = max(60, int(math.ceil(
        spec["max_runtime_s"] * scale)) + 60)
    from . import spec as spec_mod
    return spec_mod.from_dict(data, source="%s (scout x%.4g)"
                              % (spec.source, scale))


def representativeness(scout, campaign):
    """Differences that would make a calibration not carry over."""
    a, b = _fingerprint(scout), _fingerprint(campaign)
    differences = {k: {"scout": a[k], "campaign": b[k]}
                   for k in MATERIAL if a[k] != b[k]}
    return {"representative": not differences, "differences": differences}


def calibrate(work_units_done, elapsed_seconds, spec, hourly=None,
              overhead_seconds=None, source="scout", gpu_used=None):
    """Throughput and unit cost MEASURED, with overhead kept separate.

    `elapsed_seconds` is compute time only -- the module's own start-to-end
    -- so that scaling to a longer campaign multiplies compute and adds
    overhead ONCE, instead of scaling the fixed cost too. Getting that
    backwards is how a long campaign's estimate comes out high and a
    short one's comes out low.
    """
    if work_units_done <= 0:
        raise ValueError("calibration needs a positive work-unit count")
    if elapsed_seconds <= 0:
        raise ValueError("calibration needs a positive elapsed time")
    gpu = spec["gpu"]
    rate = hourly if hourly is not None else cost_mod.hourly_for(
        gpu.get("class")) * int(gpu.get("count", 1))
    overhead = (cost_mod.overhead_seconds(include_canary=bool(spec["canary"]))
                if overhead_seconds is None else float(overhead_seconds))
    per_unit_s = elapsed_seconds / float(work_units_done)
    return {
        "source": source,
        "work_units_done": float(work_units_done),
        "work_unit_name": (spec.get("work_units") or {}).get("name"),
        "compute_seconds": float(elapsed_seconds),
        "seconds_per_unit": per_unit_s,
        "units_per_second": 1.0 / per_unit_s,
        "hourly_usd": rate,
        "usd_per_unit": per_unit_s / 3600.0 * rate,
        "overhead_seconds": overhead,
        "measured_with_instrumentation": True,
        # The card the scout ACTUALLY got. A spec may declare alternatives,
        # and seconds per unit on an RTX 4090 say little about an A4000.
        "gpu_used": gpu_used or gpu.get("class"),
    }


def project_from_calibration(calibration, requested_units, pods=1,
                             margin=DEFAULT_MARGIN,
                             teardown_reserve_s=DEFAULT_TEARDOWN_RESERVE_S):
    """Campaign cost from measured throughput. Overhead is per POD.

    `expected_usd` is the EXPECTATION: compute plus the calibration's own
    overhead. The teardown reserve is NOT in it. A scout's measured
    overhead already contains a real teardown, so adding the reserve to
    the expectation counted teardown twice -- Iteration 2's campaign came
    in 16% under a calibrated estimate for exactly that reason. The reserve
    is a GUARDRAIL and is added only to `usd_with_margin`, which is what a
    ceiling is set from and what the decision is taken on.
    """
    compute_s = calibration["seconds_per_unit"] * float(requested_units)
    per_pod_compute = compute_s / max(1, pods)
    per_pod_expected = per_pod_compute + calibration["overhead_seconds"]
    rate = calibration["hourly_usd"]
    usd = pods * per_pod_expected / 3600.0 * rate
    reserve_usd = pods * teardown_reserve_s / 3600.0 * rate
    return {
        "requested_units": float(requested_units),
        "pods": int(pods),
        "compute_seconds_total": compute_s,
        "per_pod_seconds": per_pod_expected + teardown_reserve_s,
        "per_pod_expected_seconds": per_pod_expected,
        "overhead_seconds_per_pod": calibration["overhead_seconds"],
        "teardown_reserve_s": teardown_reserve_s,
        "teardown_reserve_usd": reserve_usd,
        "expected_usd": usd,
        "margin": margin,
        "usd_with_margin": usd * (1.0 + margin) + reserve_usd,
        "usd_per_unit": calibration["usd_per_unit"],
    }


def plan_campaign(spec, calibration, requested_units, ceiling_usd, pods=1,
                  margin=DEFAULT_MARGIN,
                  teardown_reserve_s=DEFAULT_TEARDOWN_RESERVE_S,
                  campaign_spec=None, accept_differences=False,
                  preregistered_usd=None):
    """PROCEED, REFUSE or REFUSE-with-proposal. Never a silent reshape.

    The decision is on `usd_with_margin`, not on the bare estimate: a
    ceiling met by the estimate alone is a ceiling that a 7% miss turns
    into a truncated run.
    """
    scout_of = campaign_spec or spec
    rep = representativeness(spec, scout_of) if campaign_spec else \
        {"representative": True, "differences": {}}
    if not rep["representative"] and not accept_differences:
        raise CampaignRefused(
            "the calibration came from a workload that differs from the "
            "campaign in %s. Re-run a representative scout, or pass "
            "accept_differences=True to say in as many words that these "
            "differences do not change seconds per unit."
            % ", ".join(sorted(rep["differences"])))

    # A calibration measured on one card does not price another. The
    # campaign must be pinned to the card the scout ran on, or the caller
    # must accept the difference in as many words.
    measured_on = calibration.get("gpu_used")
    campaign_gpu = spec["gpu"].get("class")
    campaign_alts = [g for g in spec["gpu"].get("alternatives", [])
                     if g != measured_on]
    if measured_on and not accept_differences and (
            campaign_gpu != measured_on or campaign_alts):
        raise CampaignRefused(
            "the calibration was measured on %s, but the campaign may run on "
            "%s. Pin the campaign to %s (class, no other alternatives), or "
            "pass accept_differences=True."
            % (measured_on, ", ".join([campaign_gpu] + campaign_alts),
               measured_on))

    projection = project_from_calibration(
        calibration, requested_units, pods=pods, margin=margin,
        teardown_reserve_s=teardown_reserve_s)
    fits = projection["usd_with_margin"] <= ceiling_usd

    # The largest workload that WOULD fit, as information for the seat.
    # It is a proposal, not an instruction, and nothing here acts on it.
    # The exact inverse of `usd_with_margin`: margin on the expectation,
    # reserve added once, outside it.
    rate = max(calibration["hourly_usd"], 1e-12)
    reserve_usd = max(1, pods) * teardown_reserve_s / 3600.0 * rate
    budget_per_pod_s = (max(0.0, ceiling_usd - reserve_usd)
                        / (1.0 + margin)) * 3600.0 / rate / max(1, pods)
    usable_s = budget_per_pod_s - calibration["overhead_seconds"]
    affordable_units = max(0.0, usable_s * pods
                           / calibration["seconds_per_unit"])

    out = {
        "decision": "PROCEED" if fits else "REFUSE",
        "module": spec.identity,
        "ceiling_usd": float(ceiling_usd),
        "calibrated_estimate": projection,
        "representativeness": rep,
        "accepted_differences": bool(accept_differences)
        if not rep["representative"] else None,
        "fits": fits,
    }
    if preregistered_usd is not None:
        # Both go in the receipt. The gap between them is the number that
        # tells a later reader whether the planning worked.
        out["preregistered_estimate"] = {"expected_usd": float(preregistered_usd)}
        out["estimate_error"] = (
            (projection["expected_usd"] - preregistered_usd)
            / preregistered_usd if preregistered_usd else None)
    if not fits:
        out["proposal"] = {
            "affordable_units": affordable_units,
            "fraction_of_request": (affordable_units
                                    / float(requested_units)
                                    if requested_units else None),
            "note": ("This is what the ceiling affords. The controller does "
                     "NOT reshape the workload: adopting a smaller campaign "
                     "is the seat's decision, and silently running a "
                     "different experiment to fit a budget would make the "
                     "result mean something other than what was asked.")}
        out["shortfall_usd"] = projection["usd_with_margin"] - ceiling_usd
    out["recommended_controller_ceiling_usd"] = projection["usd_with_margin"]
    return out


def render(plan):
    lines = ["CAMPAIGN PLAN  %s  ->  %s" % (plan["module"], plan["decision"])]
    est = plan["calibrated_estimate"]
    lines.append("  requested        %.6g units across %d pod(s)"
                 % (est["requested_units"], est["pods"]))
    lines.append("  calibrated       $%.4f expected, $%.4f with %.0f%% margin"
                 % (est["expected_usd"], est["usd_with_margin"],
                    100 * est["margin"]))
    lines.append("  per pod          %.0f s compute + %.0f s overhead + "
                 "%.0f s teardown reserve"
                 % (est["per_pod_seconds"] - est["overhead_seconds_per_pod"]
                    - est["teardown_reserve_s"],
                    est["overhead_seconds_per_pod"],
                    est["teardown_reserve_s"]))
    lines.append("  unit cost        $%.6g per unit" % est["usd_per_unit"])
    if "preregistered_estimate" in plan:
        lines.append("  preregistered    $%.4f  (calibration differs by %+.1f%%)"
                     % (plan["preregistered_estimate"]["expected_usd"],
                        100 * (plan["estimate_error"] or 0.0)))
    lines.append("  ceiling          $%.4f" % plan["ceiling_usd"])
    lines.append("  RECOMMENDED controller ceiling $%.4f"
                 % plan["recommended_controller_ceiling_usd"])
    rep = plan["representativeness"]
    if not rep["representative"]:
        lines.append("  NOT REPRESENTATIVE: %s"
                     % ", ".join(sorted(rep["differences"])))
    if plan["decision"] == "REFUSE":
        p = plan["proposal"]
        lines.append("  SHORTFALL        $%.4f" % plan["shortfall_usd"])
        lines.append("  the ceiling affords %.6g units (%.1f%% of the request)"
                     % (p["affordable_units"],
                        100 * (p["fraction_of_request"] or 0.0)))
        lines.append("  " + p["note"])
    return "\n".join(lines)
