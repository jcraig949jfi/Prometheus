"""Cost model: a pod costs more than its compute.

The hourly GPU price is the least interesting number. What a seat
actually pays is

    startup + bootstrap + dependency install + compute + teardown

and on a short experiment the overhead dominates. AETH-02's own numbers
make the point: a 1,300 s calibration pod spent roughly 90 s before the
science began, so ~7% of that bill bought no compute at all. For a
60 s workload the same overhead would be 60%.

OVERHEAD DEFAULTS ARE MEASURED, NOT GUESSED, and are marked with their
provenance so a later reader can tell an estimate from an observation.
They are updated only from real runs.

The denominator is the module's own: site-ticks for Aether, candidates
or evaluations for another seat. The platform must not impose one.
"""

# Observed on AETH-01/AETH-02 runs on this account, A40 SECURE.
# Replace from measurement; do not tune to make a projection look good.
OVERHEAD_S = {
    "accept": 1.0,        # create request -> pod accepted (measured ~1 s)
    "provision": 20.0,    # accepted -> machine available (inferred)
    "bootstrap": 40.0,    # download, checksum, pip install (inferred)
    "canary": 12.0,       # 300-case GPU canary (measured 10.9-12.9 s)
    "teardown": 5.0,      # terminate request -> absence confirmed (measured)
}
OVERHEAD_PROVENANCE = {
    "accept": "measured, create->201 in AETH-02 launches",
    "provision": "INFERRED from canary-ready latency, not isolated",
    "bootstrap": "INFERRED from the same interval; not yet decomposed",
    "canary": "measured, receipt gpu_kernel_seconds 10.95-12.94",
    "teardown": "measured, terminate ACK to absence confirmed",
}

# Quoted hourly rates. Not authoritative: the provider is.
HOURLY_USD = {
    "NVIDIA A40": 0.49,
    "NVIDIA RTX A4000": 0.17,
    "NVIDIA RTX A5000": 0.26,
    "NVIDIA GeForce RTX 4090": 0.34,
    "NVIDIA L4": 0.43,
}
DEFAULT_HOURLY_USD = 0.49


def hourly_for(gpu_class):
    return HOURLY_USD.get(gpu_class, DEFAULT_HOURLY_USD)


def overhead_seconds(include_canary=True):
    total = sum(v for k, v in OVERHEAD_S.items()
                if include_canary or k != "canary")
    return total


def project(spec, workload_seconds=None, hourly=None, include_canary=True):
    """Projected cost, with overhead and compute reported separately.

    `workload_seconds` is the module's own estimate. When absent the
    projection uses `max_runtime_s`, which is a CEILING and is labelled
    as such rather than quietly presented as an expectation.
    """
    gpu = spec["gpu"]
    rate = hourly if hourly is not None else hourly_for(gpu.get("class"))
    rate *= int(gpu.get("count", 1))
    bounded = workload_seconds is None
    compute_s = float(spec["max_runtime_s"] if bounded else workload_seconds)
    over_s = overhead_seconds(include_canary)
    total_s = compute_s + over_s
    usd = total_s / 3600.0 * rate

    out = {
        "gpu_class": gpu.get("class"),
        "gpu_count": int(gpu.get("count", 1)),
        "hourly_usd": round(rate, 4),
        "overhead_s": round(over_s, 1),
        "overhead_breakdown_s": dict(OVERHEAD_S) if include_canary else
            {k: v for k, v in OVERHEAD_S.items() if k != "canary"},
        "compute_s": round(compute_s, 1),
        "compute_is_ceiling": bounded,
        "total_s": round(total_s, 1),
        "usd_total": round(usd, 4),
        "usd_overhead": round(over_s / 3600.0 * rate, 4),
        "usd_compute": round(compute_s / 3600.0 * rate, 4),
        "overhead_fraction": round(over_s / total_s, 4) if total_s else None,
        "usd_per_pod_minute": round(rate / 60.0, 6),
    }
    wu = spec.get("work_units")
    if wu:
        units = float(wu["estimate"])
        out["work_units"] = {
            "name": wu["name"],
            "estimate": units,
            "usd_per_unit": usd / units if units else None,
            "usd_per_1e9_units": (usd / units * 1e9) if units else None,
            "units_per_usd": (units / usd) if usd else None,
        }
    return out


def actual(elapsed_s, hourly, work_units=None, phases=None):
    """Measured cost of a completed run.

    ESTIMATED, not reconciled. Computed from measured wall time at a
    quoted rate; it is not provider billing data and must never be
    reported as though it were. A receipt says `billing_reconciled:
    false` unless the provider was actually asked.
    """
    usd = elapsed_s / 3600.0 * hourly
    out = {
        "elapsed_s": round(elapsed_s, 1),
        "hourly_usd": hourly,
        "usd_estimated": round(usd, 5),
        "billing_reconciled": False,
        "basis": "measured wall time at a quoted rate; no provider billing "
                 "data was obtained",
    }
    if phases:
        out["phases_s"] = {k: round(v, 1) for k, v in phases.items()}
        known = sum(phases.values())
        out["unaccounted_s"] = round(elapsed_s - known, 1)
    if work_units:
        units = float(work_units.get("actual") or work_units.get("estimate") or 0)
        if units > 0:
            out["work_units"] = {
                "name": work_units["name"],
                "actual": units,
                "usd_per_unit": usd / units,
                "usd_per_1e9_units": usd / units * 1e9,
            }
    return out
