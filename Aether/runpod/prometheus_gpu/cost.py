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
    # MEASURED through the platform's own launch path: Iteration 1 (RTX 4090,
    # hello-gpu-20260924T212427Z) and Iteration 2 (RTX A4000, receipts
    # gpu-load-scout-20260926T065221Z and gpu-load-20260926T065409Z).
    "accept": 1.5,         # create call -> id returned
    "provision": 2.3,      # create accepted -> pod shell running (clock-synced)
    "bootstrap": 8.0,      # fetch, verify, unpack, dependency install
    "canary": 1.2,         # the DECLARED canary; scales with what it does
    "module_setup": 1.5,   # module start -> its own work loop begins
    "end_detection": 5.0,  # module end -> controller notices; ~ watch poll / 2
    "retrieval": 5.3,      # artifacts back; SCALES WITH BYTES (8 MB here)
    "teardown": 2.2,       # terminate request -> absence confirmed
}
# The spread that matters more than the median. Iteration 1 measured the
# same bootstrap at 6 s and at over 300 s on consecutive flights with the
# same image, wheels and GPU class, so the dependency install is a
# high-variance term and a point estimate of it is misleading. This is why
# the controller waits on PROGRESS rather than on a deadline.
OVERHEAD_OBSERVED_RANGE_S = {
    "accept": (1.1, 2.9),
    "provision": (2.1, 22.1),
    "bootstrap": (6.0, 305.0),
    "end_detection": (0.4, 8.8),
    "retrieval": (0.6, 5.3),
    "teardown": (1.1, 4.1),
}
OVERHEAD_PROVENANCE = {
    "accept": "measured, create_call_s 1.745/2.947 (I1), 1.208/1.115 (I2)",
    "provision": "MEASURED with the pod clock synchronised (min-RTT offset "
                 "against /_clock, +/-0.25 s): 2.14 s and 2.29 s (I2). "
                 "Then 22.1 s (L4 scout) and 2.82 s (L4 campaign): it is a "
                 "property of the HOST the pod lands on, not of the card. "
                 "Iteration 1's '<= 24 s' bound was almost all PROXY "
                 "reachability, which overlaps the bootstrap and is not "
                 "billed separately; see FAILURE_PLAYBOOK entry 21",
    "bootstrap": "measured on the pod's clock: 6.0 (I1), 8.0 and 7.7 (I2, "
                 "excluding canary); observed up to 305 s on an identical "
                 "configuration -- see OVERHEAD_OBSERVED_RANGE_S",
    "canary": "measured, 1.0 (I1), 1.24/1.18 (I2). A property of the "
              "declared canary, not of the platform",
    "module_setup": "measured, I2 campaign: module elapsed 561.98 s minus "
                    "its loop 560.67 s. A property of the module",
    "end_detection": "measured 8.8 s at a 10 s watch poll and 0.39 s at a "
                     "3 s poll (I2); expected ~poll/2. A property of the "
                     "controller's poll, and cheap to shrink",
    "retrieval": "measured 5.28 s for 8.39 MB (I2 campaign), 0.56 s for "
                 "1.2 kB (I1); the proxy moved 8 MB at 5.4 MB/s",
    "teardown": "measured, terminate ACK to absence confirmed",
}
# Quoted hourly rates. Not authoritative: the provider is.
HOURLY_USD = {
    "NVIDIA A40": 0.49,
    "NVIDIA RTX A4000": 0.17,
    "NVIDIA RTX A5000": 0.26,
    "NVIDIA GeForce RTX 4090": 0.34,
    "NVIDIA L4": 0.43,
    # Quoted by the provider's own stock query, 2026-09-26 (Iteration 3):
    # the only SECURE card in stock while five others refused.
    "NVIDIA RTX 4000 Ada Generation": 0.28,
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
        # The reported total is the sum of the reported PARTS. Rounding each
        # independently left a breakdown that did not add up, which in a
        # money report is a defect however small the residue.
        "usd_total": round(round(over_s / 3600.0 * rate, 4)
                           + round(compute_s / 3600.0 * rate, 4), 4),
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
